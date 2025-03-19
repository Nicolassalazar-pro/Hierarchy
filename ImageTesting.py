from flask import Flask, request, jsonify
from sklearn.cluster import KMeans
from PIL import Image
import numpy as np
import pytesseract
import webcolors
import cv2

# pytesseract.pytesseract.tesseract_cmd = r'D:\Programs\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def closest_color(requested_color):
    """
    Args: Requested color.
    Output: Closest color from the list of webcolors.
    """
    min_colors = {}
    for name in webcolors.names("css3"):
        r_c, g_c, b_c = webcolors.name_to_rgb(name)
        rd = (r_c - requested_color[0]) ** 2
        gd = (g_c - requested_color[1]) ** 2
        bd = (b_c - requested_color[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]

def get_color_name(rgb_code):
    """
    Args: RGB code.
    Output: Name of the color.
    """
    try:
        hex_value = webcolors.rgb_to_hex(rgb_code)
        return webcolors.hex_to_name(hex_value)
    except ValueError:
        return closest_color(rgb_code)

# Main function 
def ocr_from_color(image):
    """
    Args: Cropped image with the color area lightened.
    Output: Text extracted from the image.
    """
    image_cropped = image

    background_color = max(image_cropped.getcolors(image_cropped.size[0] * image_cropped.size[1])) # This not works correctly with dark mode.
    background_color = get_color_name(background_color[1][0:3])
    
    extracted_text = pytesseract.image_to_string(image_cropped, lang="eng")
    cleaned_text = extracted_text.strip()
    
    background_color = str(background_color)

    return background_color, cleaned_text

def remove_text(img, text_color_threshold=222):
    
    # Read the image
    if img is None:
        raise ValueError(f"Could not open or find the image")
    
    # Convert to grayscale for text detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Create a mask for text pixels (dark pixels)
    text_mask = gray < text_color_threshold
    
    # Create a dilated version of the text mask to get neighboring pixels
    kernel = np.ones((5, 5), np.uint8)  
    result = img.copy()
    
    # For each connected component in the text mask
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(text_mask.astype(np.uint8), connectivity=8)
    
    for label in range(1, num_labels):  # Skip label 0 (background)
        # Get pixels for this text component
        component_mask = (labels == label)
        
        # Find the surrounding non-text pixels for this component
        component_dilated = cv2.dilate(component_mask.astype(np.uint8), kernel, iterations=3)
        surrounding_mask = component_dilated.astype(bool) & ~text_mask
        
        if np.any(surrounding_mask):
            # Calculate the average color of surrounding pixels
            avg_color = np.mean(img[surrounding_mask], axis=0).astype(np.uint8)
            
            # Replace text pixels with the average surrounding color
            result[component_mask] = avg_color
    
    return result

def crop_color_region(og_img, img, num_colors=5, tolerance=30, offset=0):

    # Convert to RGB (from BGR)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    og_img_rgb = cv2.cvtColor(og_img, cv2.COLOR_BGR2RGB)
    
    height, width = og_img_rgb.shape[:2]

    # Reshape the image to be a list of pixels
    pixels = img_rgb.reshape(-1, 3)
    
    # Use K-means to find the dominant colors
    kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
    kmeans.fit(pixels)
    
    # Get the dominant colors
    colors = kmeans.cluster_centers_.astype(int)
    
    # Calculate the count of pixels for each color
    labels = kmeans.labels_
    color_counts = np.bincount(labels)
    
    # Sort colors by count (excluding white/very light colors)
    white_threshold = 240  # Threshold to identify near-white colors
    color_info = []
    
    for i, color in enumerate(colors):
        # Skip if the color is near-white (all channels high)
        if np.all(color > white_threshold):
            continue
        
        # Calculate color saturation (difference between max and min channel)
        color_range = np.max(color) - np.min(color)
        
        # Skip low-saturation colors (grays)
        if color_range < 30:
            continue
            
        color_info.append({
            'color': color,
            'count': color_counts[i],
            'saturation': color_range
        })
    
    # If no suitable colors found, try again with different parameters
    if not color_info:
        print("No distinct colors found. Trying with different parameters...")
        return crop_color_region(og_img, img, num_colors + 2, tolerance + 10)
    
    # Sort by count * saturation (to prioritize distinct, common colors)
    color_info.sort(key=lambda x: x['count'] * x['saturation'], reverse=True)
    
    # Get the most dominant non-white, saturated color
    target_color = color_info[0]['color']
    
    # Create a mask for pixels similar to the target color
    lower_bound = np.maximum(0, target_color - tolerance)
    upper_bound = np.minimum(255, target_color + tolerance)
    
    mask = cv2.inRange(img_rgb, lower_bound, upper_bound)
    
    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        print("No contours found. Trying with increased tolerance...")
        return crop_color_region(og_img, img, num_colors, tolerance + 20)
    
    # Find the largest contour (the main color region)
    largest_contour = max(contours, key=cv2.contourArea)
    
    # Get the bounding rectangle
    x, y, w, h = cv2.boundingRect(largest_contour)
    
    # Crop the image to the bounding rectangle
    x_start = max(0, x - offset)
    y_start = max(0, y - offset)
    x_end = min(width, x + w + offset)
    y_end = min(height, y + h + offset)
    cropped = og_img_rgb[y_start:y_end, x_start:x_end]
    
    # Save the cropped image
    cropped_pil = Image.fromarray(cropped)
    
    # Return the coordinates for reference
    return cropped_pil

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/get-text', methods=['POST'])
def get_text():
    # Check if the post request has the file part
    if 'image' not in request.files:
        return jsonify({'error': 'No image part in the request'}), 400
    
    image = request.files['image']

    if (not(image and allowed_file(image.filename))): return jsonify({'error': 'File type not allowed'}), 400
    if image.filename == '': return jsonify({'error': 'No selected file'}), 400

    file_bytes = np.frombuffer(image.read(), np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    CLEANED_IMAGE = remove_text(img)

    CROPPED_IMAGE = crop_color_region(img, CLEANED_IMAGE)
    Color, Text = ocr_from_color(CROPPED_IMAGE)

    return jsonify({Color : Text,})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
