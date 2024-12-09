from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import qrcode
from werkzeug.utils import secure_filename
import socket

# Configure Flask app
app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    """Check if the file type is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Home page showing the QR code and uploaded files."""
    server_ip = get_local_ip()
    upload_url = f"http://{server_ip}:5000/upload"

    # Generate QR Code
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(upload_url)
    qr.make(fit=True)
    qr_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'qr_code.png')
    qr.make_image(fill="black", back_color="white").save(qr_image_path)

    # List all uploaded files
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    files = [f for f in files if f != 'qr_code.png']  # Exclude QR code from the list

    return render_template('index.html', qr_code_url=url_for('uploaded_file', filename='qr_code.png'), upload_url=upload_url, files=files)


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Handle file uploads."""
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part', 400
        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400
        if not allowed_file(file.filename):
            return 'Unsupported file type', 400
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

    if request.method == 'GET':
        return render_template('upload.html')

    return redirect(url_for('index'))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files or the QR code."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


def get_local_ip():
    """Get the local IP address of the server."""
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
