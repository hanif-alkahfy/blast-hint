import cv2
import numpy as np

# --- Konfigurasi ---
img_path = './assets/test_image_2.png'
grid_size = 8
resize_dim = 512
crop_coords = (230, 420, 1400, 1600)  # Crop agar tepat kotak 8x8

# --- Baca & Potong Gambar ---
img = cv2.imread(img_path)
if img is None:
    raise FileNotFoundError(f"Gambar tidak ditemukan: {img_path}")

x1, y1, x2, y2 = crop_coords
cropped = img[y1:y2, x1:x2]
img_resized = cv2.resize(cropped, (resize_dim, resize_dim))
gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)

# --- Adaptive Threshold ---
binary = cv2.adaptiveThreshold(gray, 255,
                               cv2.ADAPTIVE_THRESH_MEAN_C,
                               cv2.THRESH_BINARY_INV,
                               11, 3)

# --- Ukuran sel ---
cell_size = resize_dim // grid_size

# --- Deteksi Isi Grid ---
grid = []
for y in range(grid_size):
    row = []
    for x in range(grid_size):
        # Ambil hanya bagian tengah sel (60% dari ukuran sel)
        pad = int(cell_size * 0.2)
        x_start = x * cell_size + pad
        y_start = y * cell_size + pad
        x_end = (x + 1) * cell_size - pad
        y_end = (y + 1) * cell_size - pad

        cell = binary[y_start:y_end, x_start:x_end]
        nonzero_count = cv2.countNonZero(cell)
        total_pixels = cell.shape[0] * cell.shape[1]

        filled_ratio = nonzero_count / total_pixels
        value = 1 if filled_ratio > 0.1 else 0  # Ubah threshold sesuai kebutuhan
        row.append(value)
    grid.append(row)

# --- Print hasil ---
for row in grid:
    print(row)

# --- Visualisasi Grid ---
for y in range(grid_size):
    for x in range(grid_size):
        top_left = (x * cell_size, y * cell_size)
        bottom_right = ((x + 1) * cell_size, (y + 1) * cell_size)
        color = (0, 255, 0) if grid[y][x] == 1 else (255, 0, 0)
        cv2.rectangle(img_resized, top_left, bottom_right, color, 2)

cv2.imshow("Detected Grid", img_resized)
cv2.imshow("Binary Image", binary)
cv2.waitKey(0)
cv2.destroyAllWindows()
