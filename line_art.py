import cv2
import numpy as np
import os

class LineArtProcessor:
    def __init__(self, image_path):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file '{image_path}' not found")

        self.original_image = cv2.imread(image_path)
        if self.original_image is None:
            raise ValueError(f"Failed to load image '{image_path}'")

        self.process_image()

    def process_image(self):
        # Convert to grayscale
        self.gray_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)

        # Apply CLAHE
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
        self.gray_image = clahe.apply(self.gray_image)

        # Enhance contrast
        self.gray_image = cv2.convertScaleAbs(self.gray_image, alpha=1.5, beta=10)

        # Apply bilateral filter
        self.gray_image = cv2.bilateralFilter(self.gray_image, 9, 35, 35)

        # Edge detection
        edges_list = []
        for sigma in [0.3, 0.6, 0.9]:
            blurred = cv2.GaussianBlur(self.gray_image, (0, 0), sigma)
            edges = cv2.Canny(blurred, 15, 80)
            edges_list.append(edges)
            edges_fine = cv2.Canny(blurred, 5, 50)
            edges_list.append(edges_fine)

        self.edges = np.maximum.reduce(edges_list)
        kernel = np.ones((1,1), np.uint8)
        self.edges = cv2.dilate(self.edges, kernel, iterations=1)

    def generate_points(self):
        points = []
        edge_points = np.where(self.edges > 0)

        for y, x in zip(edge_points[0], edge_points[1]):
            points.append((x, y))

        if not points:
            raise ValueError("No edges detected in the image")

        return self.sort_points(points)

    def sort_points(self, points):
        # ... (keep your existing sorting logic)
        return sorted_points