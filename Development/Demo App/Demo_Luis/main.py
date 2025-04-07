import os
from dummyTest import readImage
from flask import Flask, render_template, url_for, request, flash, redirect, send_from_directory
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "images"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
msg = None

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.add_url_rule("/uploads/<name>", endpoint="download_file", build_only=True)

def allowed_file(filename):
    ans = False
    for i in range(len(filename)):
        if filename[i - 1] == ".":
            print(filename[i:])
            if filename[i:] in ALLOWED_EXTENSIONS:
                ans = True
                break
    return ans

@app.route("/", methods=["GET", "POST"])
def home():
    global msg
    msg = ""
    if request.method == "POST":
        if "file" not in request.files:
            msg = "No file part :c"
        
        file = request.files["file"]
        
        if file.filename == "":
            msg = "No file detected."
        elif file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            return redirect(url_for("download_file", name=filename))
        else:
            msg = "Not a valid file, please upload another file."
    return render_template("index.html", msg=msg, text="")

@app.route("/uploads/<name>")
def download_file(name):
    global msg
    msg = "The file was uploaded successfully!"
    send_from_directory(app.config["UPLOAD_FOLDER"], name)
    print(1)
    return redirect(url_for("show_text", name=name))

@app.route("/processing/<name>", methods=["GET", "POST"])
def show_text(name):
    global msg
    display_msg = ""
    text = ""
    if request.method == "GET":
        if msg != None:
            display_msg = msg
            msg = None
        text = readImage(name, 1)
    else:
        return redirect(url_for("home"))
    return render_template("index.html", msg=display_msg, text=text)

if __name__ == "__main__":
    app.run(debug=True)