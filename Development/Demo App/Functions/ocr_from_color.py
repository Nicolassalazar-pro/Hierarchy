import pytesseract
import json
import webcolors
from PIL import Image

# Colors aux functions
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
    image_cropped = Image.open("images_test/{}".format(image))
    background_color = max(image_cropped.getcolors(image_cropped.size[0] * image_cropped.size[1])) # This not works correctly with dark mode.
    background_color = get_color_name(background_color[1][0:3])
    
    extracted_text = pytesseract.image_to_string(image_cropped, lang="eng")
    cleaned_text = extracted_text.strip()
    
    background_color = str(background_color)
    text = {background_color: cleaned_text}
    
    json_object = json.dumps(text)
    return json_object

print(ocr_from_color("Test2_Cropped.png"))