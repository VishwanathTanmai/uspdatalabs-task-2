import torch
import cv2
import numpy as np
import os
from PIL import Image

class VisionService:
    def __init__(self):
        # Load YOLOv5 model (using torch.hub)
        # Using 'yolov5x' (Extra Large) for maximum accuracy (approx 800+ layers equiv)
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5x', pretrained=True)
        self.model.conf = 0.15  # Deep analysis: Very low confidence to catch everything

    def process_image(self, image_path):
        # 1. Object Detection
        # augment=True enables Test Time Augmentation (TTA) for better recall
        results = self.model(image_path, augment=True)
        
        # Get pandas dataframe of results
        df = results.pandas().xyxy[0]
        
        objects_detected = []
        for index, row in df.iterrows():
            objects_detected.append({
                'name': row['name'],
                'confidence': float(row['confidence']),
                'bbox': [row['xmin'], row['ymin'], row['xmax'], row['ymax']]
            })

        # 2. OpenCV Analysis (Color, Shape of the main object or whole image)
        # Read image
        img = cv2.imread(image_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Dominant Color
        dominant_color = self.get_dominant_color(img_rgb)
        
        # Shape Analysis (Simple contours)
        shapes = self.detect_shapes(img)
        
        # Dimensions (Pixel dimensions)
        height, width, _ = img.shape
        
        # Uniqueness (Simple histogram comparison or feature count as proxy)
        unique_score = self.calculate_uniqueness(img)

        # Draw bounding boxes for return image
        annotated_img = np.squeeze(results.render()) # results.render() returns a list of arrays
        
        # Save processed image
        processed_filename = 'processed_' + os.path.basename(image_path)
        processed_path = os.path.join(os.path.dirname(image_path), processed_filename)
        # Convert RGB back to BGR for OpenCV saving
        cv2.imwrite(processed_path, cv2.cvtColor(annotated_img, cv2.COLOR_RGB2BGR))

        # 3. Object Extraction (Cropping)
        crops_dir = os.path.join(os.path.dirname(image_path), 'crops')
        os.makedirs(crops_dir, exist_ok=True)
        
        extracted_items = []
        for i, obj in enumerate(objects_detected):
            bbox = obj['bbox']
            # Coordinates: xmin, ymin, xmax, ymax
            xmin, ymin, xmax, ymax = map(int, bbox)
            
            # Clamp coordinates
            h, w, _ = img.shape
            xmin = max(0, xmin); ymin = max(0, ymin)
            xmax = min(w, xmax); ymax = min(h, ymax)
            
            # Crop
            crop = img[ymin:ymax, xmin:xmax]
            
            if crop.size > 0:
                crop_filename = f"crop_{i}_{os.path.basename(image_path)}"
                crop_path = os.path.join(crops_dir, crop_filename)
                cv2.imwrite(crop_path, crop)
                extracted_items.append(crop_filename)

        return {
            'objects': objects_detected,
            'dominant_color': dominant_color,
            'shapes': shapes,
            'dimensions': {'width': width, 'height': height},
            'uniqueness_score': unique_score,
            'processed_image_path': processed_filename,
            'extracted_items': extracted_items,
            'tags': [obj['name'] for obj in objects_detected]
        }

    def get_dominant_color(self, img):
        # Reshape to list of pixels
        pixels = np.float32(img.reshape(-1, 3))
        # K-Means
        n_colors = 1
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
        flags = cv2.KMEANS_RANDOM_CENTERS
        _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
        _, counts = np.unique(labels, return_counts=True)
        dominant = palette[np.argmax(counts)]
        return [int(c) for c in dominant]

    def detect_shapes(self, img):
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(gray, 50, 150)
        
        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        shape_list = []
        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.04 * peri, True)
            if len(approx) == 3:
                shape_name = "Triangle"
            elif len(approx) == 4:
                shape_name = "Rectangle"
            elif len(approx) > 4:
                shape_name = "Circle/Polygon"
            else:
                shape_name = "Unknown"
            shape_list.append(shape_name)
            
        return list(set(shape_list)) # Unique shapes

    def calculate_uniqueness(self, img):
        # Proxy: Entropy or just number of features
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        orb = cv2.ORB_create()
        kp = orb.detect(gray, None)
        return len(kp) / 100.0 # Normalized score concept

vision_service = VisionService()
