# Line Art Animator

This Python script creates an animated line art drawing from an input image. The animation shows a single continuous line being drawn to create a portrait-like representation of the input image.

## Requirements

Install the required packages using:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your input image in the same directory as the script
2. Update the image path in `line_art_animator.py`:
   ```python
   animator = LineArtAnimator("your_image.jpg")
   ```
3. Run the script:
   ```bash
   python line_art_animator.py
   ```

## Controls
- Press ESC to exit the animation
- Close the window to stop the animation

## How it works
The script uses OpenCV to detect edges in the input image and then creates a continuous line by connecting these edge points. The animation shows this line being drawn progressively, creating an artistic effect.
