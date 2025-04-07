import os
import pytesseract
from PIL import Image

def readImage(name="", option=0):
    ans = None
    if not option:
        _, _, files = next(os.walk("images"))
        for i in range(len(files)):
            image_path = "images/dummypic{}.png".format(i + 1)
            image = Image.open(image_path)

            extracted_text = pytesseract.image_to_string(image, lang="eng")
            cleaned_text = extracted_text.strip()

            if not i:
                file1 = open("images_output.txt", "w")
            else:
                file1 = open("images_output.txt", "a")
            
            file1.write(cleaned_text)
            file1.write("\n")
            file1.write("\n")
            file1.close()
    else:
        image = Image.open("images/" + name)
        
        extracted_text = pytesseract.image_to_string(image, lang="eng")
        cleaned_text = extracted_text.strip()
        
        ans = cleaned_text
    return ans
        
