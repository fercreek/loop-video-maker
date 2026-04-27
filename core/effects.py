"""
core/effects.py — Production visual effects for the video render pipeline.

v3.9-production:
  create_godray_png() — diagonal white RGBA overlay composited over every
  video frame.  Generated once per render, reused for all clips.
"""
from __future__ import annotations

import os

import numpy as np
from PIL import Image, ImageFilter


def create_godray_png(
    work_dir: str,
    width: int,
    height: int,
    corner: str = "top-left",
    alpha: float = 0.15,
    blur: int = 60,
) -> str:
    """
    Generate a diagonal god-ray RGBA PNG for compositing over video frames.

    Creates a white diagonal gradient (top-left → bottom-right) with
    Hermite smoothstep falloff and Gaussian blur.  Saved once per render
    and reused for all clips via ffmpeg [2:v] input.

    Args:
        work_dir:  Directory to save godray.png (the render _work dir)
        width:     Frame width in pixels
        height:    Frame height in pixels
        corner:    Light-source corner — only "top-left" supported for now
        alpha:     Peak opacity at the corner (0.0–1.0, default 0.15 = subtle)
        blur:      Gaussian blur radius in pixels (default 60 = soft diffusion)

    Returns:
        Absolute path to the saved godray.png
    """
    y_idx, x_idx = np.mgrid[0:height, 0:width]

    # Normalised distance from the top-left corner (0 = corner, 1 = far corner)
    dist = (x_idx / width + y_idx / height) / 2.0

    # Hermite smoothstep: gentle near source, fast falloff toward the edges
    smooth = dist ** 2 * (3 - 2 * dist)

    arr = np.zeros((height, width, 4), dtype=np.uint8)
    arr[..., :3] = 255                                                   # white ray
    arr[..., 3] = ((1.0 - smooth) * alpha * 255).astype(np.uint8)       # alpha channel

    img = (
        Image.fromarray(arr, mode="RGBA")
        .filter(ImageFilter.GaussianBlur(radius=blur))
    )
    path = os.path.join(work_dir, "godray.png")
    img.save(path)
    return path
