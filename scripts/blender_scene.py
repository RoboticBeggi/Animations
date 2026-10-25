"""Headless procedural Blender scene.

  blender -b -P scripts/blender_scene.py -- --out renders/scene --frames 120 --engine CYCLES
"""
import argparse
import math
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--out", default="//renders/scene_")
ap.add_argument("--frames", type=int, default=120)
ap.add_argument("--fps", type=int, default=30)
ap.add_argument("--res", type=int, nargs=2, default=[1920, 1080])
ap.add_argument("--engine", default="BLENDER_EEVEE", choices=["BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "CYCLES"])
ap.add_argument("--samples", type=int, default=64)
ap.add_argument("--movie", action="store_true", help="render an mp4 instead of a PNG sequence")
args = ap.parse_args(argv)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.frame_start, scene.frame_end, scene.render.fps = 1, args.frames, args.fps
scene.render.resolution_x, scene.render.resolution_y = args.res
try:
    scene.render.engine = args.engine
except TypeError:  # EEVEE was renamed across Blender versions
    scene.render.engine = "BLENDER_EEVEE_NEXT" if args.engine == "BLENDER_EEVEE" else args.engine
if scene.render.engine == "CYCLES":
    scene.cycles.samples = args.samples


def material(name, color, metallic=0.0, rough=0.35):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    return m


# floor + animated rotating torus knot
bpy.ops.mesh.primitive_plane_add(size=30)
bpy.context.object.data.materials.append(material("floor", (0.05, 0.05, 0.08), rough=0.15))
bpy.ops.mesh.primitive_torus_add(major_radius=1.2, minor_radius=0.35, location=(0, 0, 1.6))
knot = bpy.context.object
knot.data.materials.append(material("gold", (1.0, 0.65, 0.15), metallic=1.0, rough=0.2))
for f, ang in ((1, 0), (args.frames, math.tau)):
    knot.rotation_euler = (ang, ang / 2, 0)
    knot.keyframe_insert("rotation_euler", frame=f)
for fc in knot.animation_data.action.fcurves:
    for k in fc.keyframe_points:
        k.interpolation = "LINEAR"

# lighting + orbiting camera
bpy.ops.object.light_add(type="AREA", location=(3, -3, 6))
bpy.context.object.data.energy = 1200
bpy.ops.object.empty_add(location=(0, 0, 1.6))
pivot = bpy.context.object
bpy.ops.object.camera_add(location=(0, -6, 2.4))
cam = bpy.context.object
c = cam.constraints.new("TRACK_TO")
c.target, c.track_axis, c.up_axis = pivot, "TRACK_NEGATIVE_Z", "UP_Y"
cam.parent = pivot
scene.camera = cam
for f, z in ((1, 0), (args.frames, math.radians(90))):
    pivot.rotation_euler = (0, 0, z)
    pivot.keyframe_insert("rotation_euler", frame=f)

if args.movie:
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format, scene.render.ffmpeg.codec = "MPEG4", "H264"
else:
    scene.render.image_settings.file_format = "PNG"
scene.render.filepath = args.out
bpy.ops.render.render(animation=True)
