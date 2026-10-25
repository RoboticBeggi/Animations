#!/usr/bin/env bash
# System-level tools (Debian/Ubuntu). Run with sudo.
set -euo pipefail

apt-get update
apt-get install -y \
  ffmpeg imagemagick \
  gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav \
  blender synfig \
  python3-venv python3-pip nodejs npm

# OpenToonz has no apt package; install via Flatpak.
if command -v flatpak >/dev/null; then
  flatpak install -y flathub io.github.opentoonz.OpenToonz || true
else
  echo "flatpak not found: install OpenToonz manually (https://opentoonz.github.io)"
fi

# EbSynth is a closed-source desktop app: https://ebsynth.com
echo "Done. Next: npm install && pip install -r requirements.txt"
