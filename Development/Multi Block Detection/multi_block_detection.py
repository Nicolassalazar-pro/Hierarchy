import os
import json
import cv2
import shutil
import numpy as np

# Global Variables
info_colors = {}
test_number = 0

# Aux Function
def find_color_region(colors_temp, image, image_hsv, count):
    """
        Function to find the color background and the text of the image.
        It saves the cropped images in a folder named "testX" where X is the test number.
        (Parameters):
            colors_temp: Dictionary with the color name and the lower and upper limit of the color in HSV.
            image: Image to be processed.
            image_hsv: Image in HSV format.
            count: Counter for the number of cropped images.
        (Returns):
            count: Counter for the number of cropped images.
    """
    global info_colors, test_number
    for color_name, (lower_bound, upper_bound, colors_combinations) in colors_temp.items():
        layaout = cv2.inRange(image_hsv, np.array(lower_bound), np.array(upper_bound))
        contours, _ = cv2.findContours(layaout, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # The image turns into a matrix.
            
        for con in contours:
            x, y, w, h = cv2.boundingRect(con)
                
            if w > 30 and h > 15:
                # The conditional is for the size of the new cropped image.
                cropped = image[y:y+h, x:x+w]
                pic_cropped = "Text{} ({}).png".format(count + 1, color_name)
                cv2.imwrite(pic_cropped, cropped)
                
                if color_name in info_colors:
                    info_colors[color_name]["images_cropped"].append("test{}/{}".format(test_number + 1, pic_cropped))
                else:
                    info_colors[color_name] = {"images_cropped": ["test{}/{}".format(test_number + 1, pic_cropped)]}
                
                if len(colors_combinations) > 0:
                    info_colors[color_name]["combinations"] = colors_combinations
                
                try:
                    os.mkdir("test{}".format(test_number + 1))
                except FileExistsError:
                    pass
                
                shutil.move(pic_cropped, "test{}/{}".format(test_number + 1, pic_cropped))
                print("Cropped image saved as: {}".format(pic_cropped))
                count += 1
    
    return count

# Main Function
def cropped_and_detection(count_images=1, specific_test=0):
    """
        Function to process the images and colors of the highlighted text.
        It saves info in a JSON file about the cropped images and the colors detected and
        the combination of colors (if exists in the input image).
        (Parameters):
            count_images: Number of images to be processed.
            specific_test: Specific test number (image) to be processed.
    """
    global info_colors, test_number
    # Define the color range for detection (lower limit and upper limit in HSV)
    colors = {
        "yellow": ((20, 100, 100), (35, 255, 255), []),
        "green": ((40, 50, 50), (90, 255, 255), []),
        "magenta": ((140, 50, 50), (170, 255, 255), []),
        "blue": ((80, 100, 100), (130, 255, 255), []),
        "red": ((0, 100, 100), (10, 255, 255), [])
    }
    color_combinations_hsv = {
        "lime_green": ((25, 200, 200), (35, 255, 255), ["yellow", "green"]),
        "peach_orange": ((5, 150, 200), (15, 255, 255), ["yellow", "magenta"]),
        "turquoise_green": ((40, 150, 200), (50, 255, 255), ["yellow", "blue"]),
        "bright_orange": ((2, 200, 200), (12, 255, 255), ["yellow", "red"]),
        "brownish_gray": ((5, 50, 50), (15, 120, 120), ["green", "magenta"]),
        "dirty_cyan": ((45, 100, 200), (55, 200, 255), ["green", "blue"]),
        "dark_brown": ((5, 80, 50), (15, 150, 100), ["green", "red"]),
        "deep_purple": ((62, 150, 150), (72, 255, 255), ["magenta", "blue"]),
        "vivid_pink": ((75, 200, 200), (85, 255, 255), ["magenta", "red"]),
        "dark_purple": ((67, 150, 150), (77, 230, 230), ["blue", "red"])
    }
    
    if specific_test > 0:
        count_images = 1
    
    for i in range(count_images):
        # Read the image
        if specific_test > 0:
            image = cv2.imread("test_images/test{}.jpg".format(specific_test))
        else:
            image = cv2.imread("test_images/test{}.jpg".format(i + 1))
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        count = 0
        count = find_color_region(colors, image, image_hsv, count) # Finds base colors.
        count = find_color_region(color_combinations_hsv, image, image_hsv, count) # Finds mixed colors.
        
        test_number += 1
    
    file_j = open("info_colors.json", "w")
    file_j.write(json.dumps(info_colors, indent=4))
    file_j.close()
    print("Total cropped images: {}".format(count))
    print("Program completed successfully.")
    
cropped_and_detection(4)