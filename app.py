from flask import Flask, render_template, jsonify, request
import os
from line_art import LineArtProcessor

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_files = [f for f in os.listdir(current_dir) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]

        if not image_files:
            return jsonify({'error': 'No image files found'})

        image_path = os.path.join(current_dir, image_files[0])
        processor = LineArtProcessor(image_path)
        points = processor.generate_points()

        return jsonify({
            'points': [[int(x), int(y)] for x, y in points],
            'width': processor.gray_image.shape[1],
            'height': processor.gray_image.shape[0],
            'success': True
        })

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)