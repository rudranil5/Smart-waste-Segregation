import cv2
import numpy as np

def detect_plastic_bag(image_path):
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        return False
    
    # Convert to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Define color ranges for plastic detection (adjust these values)
    # For transparent/white plastic
    lower_white = np.array([0, 0, 200], dtype=np.uint8)
    upper_white = np.array([255, 50, 255], dtype=np.uint8)
    mask_white = cv2.inRange(hsv, lower_white, upper_white)
    
    # For colored plastic (example: blue plastic)
    lower_blue = np.array([100, 150, 0], dtype=np.uint8)
    upper_blue = np.array([140, 255, 255], dtype=np.uint8)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    
    # Combine masks
    combined_mask = cv2.bitwise_or(mask_white, mask_blue)
    
    # Edge detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    # Combine edges with color mask
    masked_edges = cv2.bitwise_and(edges, edges, mask=combined_mask)
    
    # Find contours
    contours, _ = cv2.findContours(masked_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Contour analysis parameters (adjust these values)
    min_area = 1000  # Minimum contour area to consider
    edge_density_threshold = 0.1  # Edge pixels vs area ratio
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > min_area:
            # Calculate edge density
            x, y, w, h = cv2.boundingRect(cnt)
            roi = masked_edges[y:y+h, x:x+w]
            edge_pixels = np.count_nonzero(roi)
            density = edge_pixels / (w * h) if (w * h) > 0 else 0
            
            # Check for characteristics of plastic bags
            if density > edge_density_threshold:
                return True
    
    return False

# Usage example
result = detect_plastic_bag(r"D:\garbage-detector\data\dataset\paper\paper591.jpg")
print("Plastic bag detected:", result)