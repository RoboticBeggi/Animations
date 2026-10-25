"""Minimal ComfyUI API client: patch a saved API-format workflow, queue it, download outputs."""
from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path


def _host() -> str:
    return os.environ.get("COMFYUI_HOST", "127.0.0.1:8188")


def apply_overrides(workflow: dict, overrides: list[str]) -> dict:
    """Patch inputs with 'NODE_ID.input=value' strings (JSON values allowed, else string)."""
    for item in overrides:
        target, _, raw = item.partition("=")
        node, _, key = target.partition(".")
        if node not in workflow:
            raise KeyError(f"node {node!r} not in workflow")
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            value = raw
        workflow[node]["inputs"][key] = value
    return workflow


def _get(path: str):
    with urllib.request.urlopen(f"http://{_host()}{path}") as r:
        return r.read()


def queue(workflow: dict) -> str:
    body = json.dumps({"prompt": workflow, "client_id": uuid.uuid4().hex}).encode()
    req = urllib.request.Request(f"http://{_host()}/prompt", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["prompt_id"]


def wait(prompt_id: str, timeout: float = 1800, poll: float = 1.5) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        hist = json.loads(_get(f"/history/{prompt_id}"))
        if prompt_id in hist:
            return hist[prompt_id]
        time.sleep(poll)
    raise TimeoutError(f"ComfyUI job {prompt_id} did not finish in {timeout}s")


def run_workflow(workflow_path: str, out_dir: str, overrides: list[str] | None = None) -> list[Path]:
    wf = apply_overrides(json.loads(Path(workflow_path).read_text()), overrides or [])
    entry = wait(queue(wf))
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    for node in entry["outputs"].values():
        for f in node.get("images", []) + node.get("gifs", []) + node.get("videos", []):
            q = urllib.parse.urlencode({"filename": f["filename"], "subfolder": f.get("subfolder", ""), "type": f.get("type", "output")})
            dest = out / f["filename"]
            dest.write_bytes(_get(f"/view?{q}"))
            saved.append(dest)
    return saved
