import cv2
import numpy as np

# --- Konfigurasi ---
img_path = './assets/test_image_2.png'
block_count = 3
block_size = 5
block_crop_coords = (230, 1670, 1400, 2170)
target_block_height = 400
display_width = 512
manual_scale = 0.85

# Koreksi kecil untuk akurasi grid
offset_correction_x = 4
offset_correction_y = 4

# --- Load Gambar ---
img = cv2.imread(img_path)
if img is None:
    raise FileNotFoundError(f"Gambar tidak ditemukan: {img_path}")

# --- Crop Area Blok ---
x1, y1, x2, y2 = block_crop_coords
cropped = img[y1:y2, x1:x2]

# --- Resize proporsional horizontal ---
crop_h, crop_w = cropped.shape[:2]
aspect_ratio = crop_w / crop_h
resize_width = int(target_block_height * aspect_ratio)
resized = cv2.resize(cropped, (resize_width, target_block_height))

# --- Binarisasi ---
gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
binary = cv2.adaptiveThreshold(
    gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
    cv2.THRESH_BINARY_INV, 11, 3)

# --- Ukuran Tiap Blok dan Sel ---
block_width = resize_width // block_count
cell_size = int((min(block_width, target_block_height) // block_size) * manual_scale)
grid_size = cell_size * block_size

# --- Deteksi dan Ekstraksi Grid ---
blocks_array = []

for i in range(block_count):
    x_start = i * block_width
    x_end = x_start + block_width
    roi = binary[:, x_start:x_end]

    contours, _ = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        blocks_array.append([[0]*block_size for _ in range(block_size)])
        continue

    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)

    # Koreksi posisi grid agar lebih akurat
    start_x = x_start + x + offset_correction_x
    start_y = y + offset_correction_y

    block_matrix = []
    for row in range(block_size):
        r = []
        for col in range(block_size):
            cx = start_x + col * cell_size
            cy = start_y + row * cell_size
            pad = int(cell_size * 0.2)

            cell = binary[cy+pad:cy+cell_size-pad, cx+pad:cx+cell_size-pad]
            if cell.shape[0] == 0 or cell.shape[1] == 0:
                r.append(0)
                continue

            nonzero = cv2.countNonZero(cell)
            total = cell.shape[0] * cell.shape[1]
            ratio = nonzero / total
            r.append(1 if ratio > 0.1 else 0)
        block_matrix.append(r)
    blocks_array.append(block_matrix)

# --- Tampilkan Data ---
for i, blk in enumerate(blocks_array):
    print(f"\nBlok {i+1}:")
    for row in blk:
        print(row)

# --- Visualisasi ---
visual = resized.copy()
for i in range(block_count):
    x_start = i * block_width
    roi = binary[:, x_start:x_start + block_width]
    contours, _ = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        continue

    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)
    start_x = x_start + x + offset_correction_x
    start_y = y + offset_correction_y

    for row in range(block_size):
        for col in range(block_size):
            top_left = (start_x + col * cell_size, start_y + row * cell_size)
            bottom_right = (start_x + (col + 1) * cell_size, start_y + (row + 1) * cell_size)
            color = (0, 255, 0) if blocks_array[i][row][col] == 1 else (255, 0, 0)
            cv2.rectangle(visual, top_left, bottom_right, color, 1)

# --- Resize dan Tampilkan ---
display_height = int(display_width / aspect_ratio)
cv2.imshow("Detected Blocks", cv2.resize(visual, (display_width, display_height)))
cv2.imshow("Binary Blocks", cv2.resize(binary, (display_width, display_height)))
cv2.waitKey(0)
cv2.destroyAllWindows()
