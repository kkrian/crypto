import time
import hashlib


import matplotlib.image as img
import matplotlib.pyplot as plt
import numpy as np


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
    encrypted_image = np.zeros_like(image)
    idx = 0
    for i in range(height):
        for j in range(width):
            zk = int((keys[idx] * (10**5)) % 256)
            encrypted_image[i, j] = image[i, j] ^ zk ^ timestamp
            idx += 1
            if idx >= len(keys):  
                idx = 0
    return encrypted_image


path = r'C:\Users\siddi\OneDrive\Desktop\New folder (2)\Projects\LORENTZ\uploads\glas-quadratisch-ga21492-taj-mahal-30x30cm-final-einzel.jpg'  # Replace with your image path
image = img.imread(path)


timestamp = int(time.time())
# print(time.time())
human_readable_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))

print(human_readable_time)
unique_id = hashlib.sha256(f"{timestamp}_{path}".encode()).hexdigest()

plt.imshow(image)
plt.axis('off')  
plt.title('Original Image')
plt.show()


xkey, ykey, zkey = lorenz_key(0.01, 0.02, 0.03, image.size // 3)


encrypted_image = xor_image(image, zkey, timestamp)


plt.imshow(encrypted_image)
plt.axis('off') 
plt.title('Encrypted Image')
plt.show()


with open("encryption_info.txt", "w") as file:
    file.write(f"Timestamp: {timestamp}\nUnique ID: {unique_id}\nHuman_Readable: {human_readable_time}")


decrypted_image = xor_image(encrypted_image, zkey, timestamp)

plt.imshow(decrypted_image)
plt.axis('off')  
plt.title('Decrypted Image')
plt.show()