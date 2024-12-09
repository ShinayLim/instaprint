import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import PyPDF2
import win32print
import win32api

# Initialize Flask app
app = Flask(__name__)

# Ensure the uploads folder exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Save the file to the uploads folder
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return render_template('settings.html', filename=filename)
    return redirect(url_for('index'))

@app.route('/print', methods=['POST'])
def print_file():
    filename = request.form['filename']
    page_size = request.form['page_size']
    page_range = request.form['page_range']
    color = request.form['color']
    
    # Construct the file path
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # If it's a PDF, adjust based on page range
    if filename.endswith('.pdf'):
        if page_range:
            start, end = map(int, page_range.split('-'))
            output_pdf_path = 'output_' + filename
            with open(file_path, 'rb') as input_pdf:
                reader = PyPDF2.PdfReader(input_pdf)
                writer = PyPDF2.PdfWriter()

                for i in range(start - 1, end):
                    writer.add_page(reader.pages[i])

                with open(output_pdf_path, 'wb') as output_pdf:
                    writer.write(output_pdf)

            file_path = output_pdf_path  # Use the new PDF for printing

    # Explicitly select the EPSON L360 printer (replace with your printer name)
    printer_name = "EPSON L360 Series"  # Ensure this is your correct printer name

    print(f"Using Printer: {printer_name}")

    # Send print job via Windows Print API
    try:
        win32api.ShellExecute(
            0, 
            "print", 
            file_path,  # Path to the file to print
            f'/d:"{printer_name}"',  # Printer to send to (EPSON L360)
            ".", 
            0  # No window
        )
        return f"Printing {filename} with selected options."
    except Exception as e:
        return f"Error printing {filename}: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
