import cv2
import numpy as np
import pygame
import random
import os
from pygame import gfxdraw
from scipy.interpolate import splprep, splev

class LineArtAnimator:
    def __init__(self, image_path, width=800, height=800):
        self.width = width
        self.height = height
        
        # Check if image exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file '{image_path}' not found. Please make sure the image exists in the current directory.")
        
        # Load and process image
        self.original_image = cv2.imread(image_path)
        if self.original_image is None:
            raise ValueError(f"Failed to load image '{image_path}'. Make sure it's a valid image file.")
        
        # Convert to grayscale
        self.gray_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        
        # Resize image while maintaining aspect ratio
        aspect_ratio = self.gray_image.shape[1] / self.gray_image.shape[0]
        if aspect_ratio > 1:
            new_width = width
            new_height = int(width / aspect_ratio)
        else:
            new_height = height
            new_width = int(height * aspect_ratio)
        
        self.gray_image = cv2.resize(self.gray_image, (new_width, new_height))
        
        # Enhanced image processing
        # Apply adaptive histogram equalization with stronger contrast
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
        self.gray_image = clahe.apply(self.gray_image)
        
        # Enhance image contrast
        self.gray_image = cv2.convertScaleAbs(self.gray_image, alpha=1.5, beta=10)
        
        # Apply bilateral filter with adjusted parameters for better edge preservation
        self.gray_image = cv2.bilateralFilter(self.gray_image, 9, 35, 35)
        
        # Multi-scale edge detection with more sensitivity
        edges_list = []
        
        # Detect edges at multiple scales with lower thresholds for more details
        for sigma in [0.3, 0.6, 0.9]:
            blurred = cv2.GaussianBlur(self.gray_image, (0, 0), sigma)
            # Lower thresholds to catch more details
            edges = cv2.Canny(blurred, 15, 80)
            edges_list.append(edges)
            
            # Add another pass with different thresholds for fine details
            edges_fine = cv2.Canny(blurred, 5, 50)
            edges_list.append(edges_fine)
        
        # Combine edges from different scales
        self.edges = np.maximum.reduce(edges_list)
        
        # Enhance fine details with smaller kernel
        kernel = np.ones((1,1), np.uint8)
        self.edges = cv2.dilate(self.edges, kernel, iterations=1)
        
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Line Art Animation")
        
        # Drawing properties
        self.points = self.generate_points()
        self.current_point = 0
        self.drawing_speed = 2
        self.line_color = (255, 255, 255)  # White lines
        self.background_color = (0, 0, 0)   # Black background
        self.cursor_color = (255, 200, 0)   # Yellow-orange cursor
        self.cursor_radius = 3
        self.cursor_glow_colors = [
            (255, 200, 0, 255),  # Core
            (255, 150, 0, 150),  # Inner glow
            (255, 100, 0, 100),  # Middle glow
            (255, 50, 0, 50)     # Outer glow
        ]
        
    def smooth_points(self, points, smoothing=0.1):
        if len(points) < 4:
            return points
        
        # Convert points to numpy array
        points = np.array(points)
        x = points[:, 0]
        y = points[:, 1]
        
        try:
            # Fit splines to x and y coordinates
            tck, u = splprep([x, y], s=smoothing, per=False)
            
            # Sample points from spline
            u_new = np.linspace(0, 1, len(points))
            smooth_points = splev(u_new, tck)
            
            return list(zip(smooth_points[0], smooth_points[1]))
        except:
            return points
        
    def generate_points(self):
        points = []
        edge_points = np.where(self.edges > 0)
        
        # Convert edge points to list of tuples
        for y, x in zip(edge_points[0], edge_points[1]):
            points.append((x, y))
            
        if not points:
            raise ValueError("No edges detected in the image. Try using a different image with more distinct features.")
        
        # Sort points to create a more continuous line
        sorted_points = []
        remaining_points = points.copy()
        
        # Find a good starting point (preferably from the top of the image)
        top_points = [p for p in points if p[1] < self.edges.shape[0] * 0.2]
        if top_points:
            current_point = min(top_points, key=lambda p: p[1])
        else:
            current_point = points[0]
            
        sorted_points.append(current_point)
        remaining_points.remove(current_point)
        
        max_distance = 10  # Reduced maximum distance for more detail
        
        while remaining_points:
            x, y = sorted_points[-1]
            
            # Find points within reasonable distance
            close_points = [(i, p) for i, p in enumerate(remaining_points)
                          if ((p[0] - x) ** 2 + (p[1] - y) ** 2) <= max_distance ** 2]
            
            if close_points:
                # Find the point that creates the smoothest line
                if len(sorted_points) > 1:
                    prev_x, prev_y = sorted_points[-2]
                    current_angle = np.arctan2(y - prev_y, x - prev_x)
                    
                    def angle_diff(p):
                        new_angle = np.arctan2(p[1][1] - y, p[1][0] - x)
                        diff = abs(new_angle - current_angle)
                        return min(diff, 2 * np.pi - diff)
                    
                    next_point = min(close_points, key=angle_diff)[1]
                else:
                    next_point = min(close_points, key=lambda p: (p[1][0] - x) ** 2 + (p[1][1] - y) ** 2)[1]
                
                sorted_points.append(next_point)
                remaining_points.remove(next_point)
            else:
                # If no close points, find the nearest remaining point
                if remaining_points:
                    next_point = min(remaining_points, 
                                   key=lambda p: (p[0] - x) ** 2 + (p[1] - y) ** 2)
                    if ((next_point[0] - x) ** 2 + (next_point[1] - y) ** 2) <= (max_distance * 2) ** 2:
                        sorted_points.append(next_point)
                        remaining_points.remove(next_point)
                    else:
                        # Start a new line from the closest point to any existing point
                        closest_to_any = min(remaining_points,
                                          key=lambda p: min((p[0] - px) ** 2 + (p[1] - py) ** 2 
                                                          for px, py in sorted_points[-10:]))
                        sorted_points.append(closest_to_any)
                        remaining_points.remove(closest_to_any)
        
        # Apply minimal smoothing to preserve details
        return self.smooth_points(sorted_points, smoothing=0.05)  # Reduced smoothing
        
    def draw_cursor(self, pos):
        x, y = int(pos[0]), int(pos[1])
        
        # Draw glowing circles from outside to inside
        for i, (r, g, b, a) in enumerate(self.cursor_glow_colors):
            radius = self.cursor_radius + (3 - i) * 2
            surf = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(surf, (r, g, b, a), (radius + 2, radius + 2), radius)
            self.screen.blit(surf, (x - radius - 2, y - radius - 2))
    
    def draw_line_segment(self, start, end):
        # Draw anti-aliased line for smoother appearance
        pygame.draw.aaline(self.screen, self.line_color,
                         (int(start[0]), int(start[1])),
                         (int(end[0]), int(end[1])))
        
        # Draw the cursor at the end point
        self.draw_cursor(end)
    
    def animate(self):
        running = True
        clock = pygame.time.Clock()
        
        # Set up the drawing surface
        self.screen.fill(self.background_color)
        
        # Calculate center offset to center the drawing
        offset_x = (self.width - self.gray_image.shape[1]) // 2
        offset_y = (self.height - self.gray_image.shape[0]) // 2
        
        # Create a surface for the permanent drawing
        drawing_surface = pygame.Surface((self.width, self.height))
        drawing_surface.fill(self.background_color)
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Add new points to the line
            for _ in range(self.drawing_speed):
                if self.current_point < len(self.points) - 1:
                    point = self.points[self.current_point]
                    next_point = self.points[self.current_point + 1]
                    
                    # Apply offset to center the drawing
                    start = (point[0] + offset_x, point[1] + offset_y)
                    end = (next_point[0] + offset_x, next_point[1] + offset_y)
                    
                    # Draw the permanent line on the drawing surface
                    pygame.draw.aaline(drawing_surface, self.line_color,
                                    (int(start[0]), int(start[1])),
                                    (int(end[0]), int(end[1])))
                    
                    self.current_point += 1
            
            # Copy the permanent drawing to the screen
            self.screen.blit(drawing_surface, (0, 0))
            
            # Draw the cursor at the current point if we're still drawing
            if self.current_point < len(self.points):
                current_pos = self.points[self.current_point]
                cursor_pos = (current_pos[0] + offset_x, current_pos[1] + offset_y)
                self.draw_cursor(cursor_pos)
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

def main():
    # List of common image extensions
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    
    # Look for image files in the current directory
    image_files = []
    for file in os.listdir('.'):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            image_files.append(file)
    
    if not image_files:
        print("No image files found in the current directory!")
        print("Please add an image file (jpg, jpeg, png, or bmp) to this directory and try again.")
        return
    
    print("\nAvailable images:")
    for i, file in enumerate(image_files, 1):
        print(f"{i}. {file}")
    
    if len(image_files) == 1:
        image_path = image_files[0]
    else:
        while True:
            try:
                choice = input("\nEnter the number of the image you want to use (or press Enter for the first image): ").strip()
                if not choice:
                    choice = "1"
                choice = int(choice)
                if 1 <= choice <= len(image_files):
                    image_path = image_files[choice - 1]
                    break
                else:
                    print("Invalid choice. Please enter a number from the list.")
            except ValueError:
                print("Please enter a valid number.")
    
    try:
        print(f"\nCreating line art animation from: {image_path}")
        animator = LineArtAnimator(image_path)
        animator.animate()
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Please try again with a different image.")

if __name__ == "__main__":
    main()
