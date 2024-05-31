from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import time
import hashlib
import matplotlib.image as img
import numpy as np
from flask import send_from_directory
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def lorenz_key(xinit, yinit, zinit, num_steps):
    dt = 0.01
    xs = np.empty(num_steps + 1)
    ys = np.empty(num_steps + 1)
    zs = np.empty(num_steps + 1)

    xs[0], ys[0], zs[0] = (xinit, yinit, zinit)
    s = 10
    r = 28
    b = 2.667

    for i in range(num_steps):
        xs[i + 1] = xs[i] + (s * (ys[i] - xs[i]) * dt)
        ys[i + 1] = ys[i] + (xs[i] * (r - zs[i]) - ys[i]) * dt
        zs[i + 1] = zs[i] + (xs[i] * ys[i] - b * zs[i]) * dt

    return xs[1:], ys[1:], zs[1:]  


def xor_image(image, keys, timestamp):
    height, width, _ = image.shape
    encrypted_image = np.zeros_like(image, dtype=np.uint8)
    idx = 0
    for i in range(height):
        for j in range(width):
            zk = int((keys[idx] * (10**5)) % 256)
            encrypted_image[i, j] = (image[i, j].astype(np.uint8) ^ zk ^ timestamp) % 256
            idx += 1
            if idx >= len(keys):
                idx = 0
    return encrypted_image

@app.route('/encrypt', methods=['POST'])
def encrypt_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file uploaded'}), 400

    file = request.files['image']
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    image = img.imread(file_path)
    timestamp = int(time.time())
    human_readable_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    unique_id = hashlib.sha256(f"{timestamp}_{file_path}".encode()).hexdigest()

    xkey, ykey, zkey = lorenz_key(0.01, 0.02, 0.03, image.size // 3)
    encrypted_image = xor_image(image, zkey, timestamp)

    _, file_ext = os.path.splitext(filename)

    encrypted_image_path = os.path.join('uploads', f"encrypted_{unique_id}{file_ext}")
    img.imsave(encrypted_image_path, encrypted_image)

    img2 = os.path.join('uploads', f"decrypted_{unique_id}{file_ext}")
    img.imsave(img2, image)

    return jsonify({
        'timestamp': timestamp,
        'unique_id': unique_id,
        'human_readable_time': human_readable_time,
        'encrypted_image_path': encrypted_image_path  # Return the relative path
    })

@app.route('/decrypt', methods=['POST'])
def decrypt_image():
    if 'encrypted_image' not in request.files:
        return jsonify({'error': 'No encrypted image file uploaded'}), 400

    file = request.files['encrypted_image']
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    encrypted_image = img.imread(file_path)

    # Retrieve the timestamp and unique_id from the request
    timestamp = request.form.get('timestamp', type=int)
    unique_id = request.form.get('unique_id')

    if not timestamp or not unique_id:
        return jsonify({'error': 'Missing timestamp or unique_id'}), 400

    human_readable_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))

    xkey, ykey, zkey = lorenz_key(0.01, 0.02, 0.03, encrypted_image.size // 3)
    decrypted_image = xor_image(encrypted_image, zkey, timestamp)
    # image path will have encrypted_something remove encrypted and replace it wtih decrypted
    _, file_ext = os.path.splitext(filename)

    decrypted_image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"decrypted_{unique_id}{file_ext}")
    # decrypted_image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename.replace('encrypted_', 'decrypted_')}")
    # img.imsave(decrypted_image_path, decrypted_image)

    return jsonify({
        'timestamp': timestamp,
        'unique_id': unique_id,
        'human_readable_time': human_readable_time,
        'decrypted_image_path': decrypted_image_path
    })

@app.route('/uploads/<path:filename>', methods=['GET'])
def serve_uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)