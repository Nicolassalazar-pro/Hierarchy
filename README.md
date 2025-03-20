# Flask Image Upload API

This project provides a Flask-based API that accepts an image file and processes it via the `/get_text` endpoint.

## Installation

To set up and run this project, follow the steps below:

### 1. Clone the Repository
```sh
git clone https://github.com/Nicolassalazar-pro/Hierarchy.git
cd Hierarchy
```

### 2. Create a Virtual Environment (Optional but Recommended)
```sh
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate    # On Windows
```

### 3. Install Dependencies
Make sure you have `pip` installed, then run:
```sh
pip install -r requirements.txt
```
This will install all necessary dependencies listed in `requirements.txt`.

If error with Tesseract on Windows, install Tesseract here:
https://github.com/UB-Mannheim/tesseract/wiki

Then assign the path of installation to
```sh
pytesseract.pytesseract.tesseract_cmd
```

Example:
```sh
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```


## Running the Flask Server

You can run it inside the Python script:
```sh
python ImageTesting.py
```

## API Endpoint: `/get_text`

### **Method:** `POST`

### **Description:**
This endpoint accepts an image file as input and processes it.

### **Request Format:**
- The request must be `multipart/form-data` and include an image file with the key `image`.

### **Example Usage:**

#### Using cURL:
```sh
curl -X POST -F "image=@path/to/image.jpg" http://127.0.0.1:5000/get_text
```

#### Using Python `requests`:
```python
import requests

url = "http://127.0.0.1:5000/get_text"
file_path = "path/to/image.jpg"

with open(file_path, "rb") as image_file:
    files = {"image": image_file}
    response = requests.post(url, files=files)

print(response.json())
```

### **Response Format:**
- **Success:**
  ```json
  {
    "[color]": "[Text Highlighted]",
  }
  ```
- **Error:**
  ```json
  {
    "error": "[Error]"
  }
  ```

## Notes
- Ensure requirements.txt is installed before running the server.
- If you encounter issues with port 5000, use a different port as mentioned above.
- If running on macOS and port conflicts occur, disable AirPlay Receiver via **System Settings > General > AirDrop & Handoff**.

## License
This project is open-source. Feel free to modify and use it as needed.

