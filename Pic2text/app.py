from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Folder where uploaded images will be saved
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Perform OCR on the uploaded image
        ocr_result = perform_ocr(file_path)

        # Save the OCR result to a text file
        text_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}.txt")
        with open(text_file_path, 'w') as text_file:
            text_file.write(ocr_result)

        return send_file(text_file_path, as_attachment=True)

def perform_ocr(image_path):
    img = Image.open(image_path)
    img = img.convert('L')  # Convert to grayscale
    img = img.filter(ImageFilter.MedianFilter())  # Apply median filter
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)  # Increase contrast

    # Perform OCR using pytesseract
    ocr_result = pytesseract.image_to_string(img, lang='eng')

    return ocr_result

if __name__ == "__main__":
    app.run(debug=True)
