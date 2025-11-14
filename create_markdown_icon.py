#!/usr/bin/env python3
"""
Create .icns file from blue1.png for Markdown Pro app
"""

import os
import subprocess
from PIL import Image

def create_iconset():
    """Create iconset from blue1.png"""

    # Load the source image
    source_image = "blue1.png"
    if not os.path.exists(source_image):
        print(f"Error: {source_image} not found")
        return False

    # Create iconset directory
    iconset_dir = "MarkdownPro.iconset"
    os.makedirs(iconset_dir, exist_ok=True)

    # Open source image
    img = Image.open(source_image)

    # Define icon sizes needed for macOS
    sizes = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png"),
    ]

    print("Creating icon sizes...")
    for size, filename in sizes:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        output_path = os.path.join(iconset_dir, filename)
        resized.save(output_path)
        print(f"  Created {filename} ({size}x{size})")

    print(f"\nIconset created at: {iconset_dir}")
    return True

def create_icns():
    """Convert iconset to .icns file using macOS iconutil"""
    iconset_dir = "MarkdownPro.iconset"
    icns_file = "MarkdownPro.icns"

    if not os.path.exists(iconset_dir):
        print(f"Error: {iconset_dir} not found")
        return False

    print(f"\nConverting to .icns...")
    try:
        subprocess.run([
            "iconutil",
            "-c", "icns",
            iconset_dir,
            "-o", icns_file
        ], check=True)

        print(f"Successfully created {icns_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating .icns file: {e}")
        return False

def main():
    print("Markdown Pro Icon Creator")
    print("=" * 40)

    # Create iconset
    if not create_iconset():
        return

    # Create .icns
    if not create_icns():
        return

    print("\n" + "=" * 40)
    print("Icon creation complete!")
    print(f"Icon file: MarkdownPro.icns")

if __name__ == "__main__":
    main()
