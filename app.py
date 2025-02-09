from flask import Flask, render_template, jsonify, request
import cv2
import numpy as np
import os
import base64
from line_art import LineArtAnimator

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    try:
        # Get current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_files = [f for f in os.listdir(current_dir) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        
        if not image_files:
            return jsonify({'error': 'No image files found'})
        
        # Process the first image
        image_path = os.path.join(current_dir, image_files[0])
        
        # Create line art animator
        animator = LineArtAnimator(image_path)
        points = animator.generate_points()
        
        # Convert points to list for JSON serialization
        points_list = [[int(x), int(y)] for x, y in points]
        
        # Get image dimensions
        height, width = animator.gray_image.shape
        
        return jsonify({
            'points': points_list,
            'width': width,
            'height': height,
            'success': True
        })
    
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
