from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import qrcode
from werkzeug.utils import secure_filename
import socket
import subprocess  # For opening the file on the server

# Configure Flask app
app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    """Home page showing the QR code for file uploads."""
    server_ip = get_local_ip()
    server_url = f"http://{server_ip}:5000/upload"
    
    # Generate QR Code
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(server_url)
    qr.make(fit=True)
    qr_image_path = os.path.join(UPLOAD_FOLDER, 'qr_code.png')
    qr.make_image(fill="black", back_color="white").save(qr_image_path)

    return render_template('index.html', qr_code_url=url_for('uploaded_file', filename='qr_code.png'), upload_url=server_url)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """File upload route."""
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part', 400
        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Open the file on the host computer
            try:
                open_file_on_host(filepath)
            except Exception as e:
                print(f"Error opening file: {e}")

            return render_template('upload_success.html', filename=filename, filepath=filepath, file_url=url_for('uploaded_file', filename=filename))
    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files or the QR code."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def open_file_on_host(filepath):
    """Open the file on the server/host computer."""
    if os.name == 'nt':  # For Windows
        os.startfile(filepath)
    elif os.name == 'posix':  # For macOS/Linux
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filepath])

def get_local_ip():
    """Get the local IP address of the server."""
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
