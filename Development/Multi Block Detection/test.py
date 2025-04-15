import cv2
import numpy as np

def cropped_and_detection(count_images=1):
    # Define the color range for detection
    colors = {
        "yellow": ((20, 100, 100), (35, 255, 255)),
        "green": ((40, 50, 50), (90, 255, 255)),
        "magenta": ((140, 50, 50), (170, 255, 255)),
        "blue": ((100, 100, 100), (130, 255, 255)),
        "red": ((0, 100, 100), (10, 255, 255))
    }
    
    for i in range(count_images):
        # Read the image
        image = cv2.imread("test_images/test{}.jpg".format(i + 1))
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        count = 0
        for color_name, (lower_bound, upper_bound) in colors.items():
            layaout = cv2.inRange(image_hsv, np.array(lower_bound), np.array(upper_bound))
            contours, _ = cv2.findContours(layaout, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for con in contours:
                x, y, w, h = cv2.boundingRect(con)
                
                if w > 30 and h > 15:
                    cropped = image[y:y+h, x:x+w]
                    pic_cropped = "Text{} ({}).png".format(count + 1, color_name)
                    cv2.imwrite(pic_cropped, cropped)
                    print("Cropped image saved as: {}".format(pic_cropped))
                    count += 1
    
    print("Total cropped images: {}".format(count))
    print("Program completed successfully.")
    
cropped_and_detection()   