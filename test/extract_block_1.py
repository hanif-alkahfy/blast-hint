import cv2
import numpy as np

# --- Konfigurasi ---
img_path = 'test_image_2.png'
block_count = 3
block_size = 5

block_crop_coords = (230, 1670, 1400, 2170)  # (x1, y1, x2, y2)
target_block_height = 400
display_width = 512
manual_scale = 0.85  # Perkecil ukuran grid

# Offset untuk masing-masing grid
#img_2
grid_offsets = [
    {"x": 110, "y": 15},    # Grid 1
    {"x": 55, "y": 95},    # Grid 2
    {"x": 80, "y": 65},   # Grid 3
]

#img_3
# grid_offsets = [
#     {"x": 110, "y": 95},    # Grid 1
#     {"x": 110, "y": 15},    # Grid 2
#     {"x": 55, "y": 65},   # Grid 3
# ]


# --- Load dan Validasi Gambar ---
img = cv2.imread(img_path)
if img is None:
    raise FileNotFoundError(f"Gambar tidak ditemukan: {img_path}")

# --- Crop area blok ---
x1, y1, x2, y2 = block_crop_coords
cropped = img[y1:y2, x1:x2]

# --- Resize proporsional horizontal untuk proses ---
crop_h, crop_w = cropped.shape[:2]
aspect_ratio = crop_w / crop_h
resize_width = int(target_block_height * aspect_ratio)
resized = cv2.resize(cropped, (resize_width, target_block_height))

# --- Binarisasi ---
gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
binary = cv2.adaptiveThreshold(
    gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
    cv2.THRESH_BINARY_INV, 11, 3)

# --- Hitung ukuran tiap blok dan sel ---
block_width = resize_width // block_count
cell_size = int((min(block_width, target_block_height) // block_size) * manual_scale)

# --- Deteksi setiap blok secara terpisah ---
blocks_array = []

for i in range(block_count):
    offset_x = grid_offsets[i]["x"]
    offset_y = grid_offsets[i]["y"]

    pad_x = (block_width - (cell_size * block_size)) // 2 + offset_x
    pad_y = (target_block_height - (cell_size * block_size)) // 2 + offset_y
    x_offset = i * block_width + pad_x

    block_matrix = []
    for y in range(block_size):
        row = []
        for x in range(block_size):
            cx = x_offset + x * cell_size
            cy = pad_y + y * cell_size
            pad = int(cell_size * 0.2)

            cell = binary[cy+pad:cy+cell_size-pad, cx+pad:cx+cell_size-pad]
            if cell.shape[0] == 0 or cell.shape[1] == 0:
                row.append(0)
                continue

            nonzero = cv2.countNonZero(cell)
            total = cell.shape[0] * cell.shape[1]
            ratio = nonzero / total if total > 0 else 0
            row.append(1 if ratio > 0.1 else 0)
        block_matrix.append(row)
    blocks_array.append(block_matrix)

# --- Print hasil ---
for i, blk in enumerate(blocks_array):
    print(f"\nBlok {i+1}:")
    for row in blk:
        print(row)

# --- Visualisasi ---
visual = resized.copy()
for i in range(block_count):
    offset_x = grid_offsets[i]["x"]
    offset_y = grid_offsets[i]["y"]

    pad_x = (block_width - (cell_size * block_size)) // 2 + offset_x
    pad_y = (target_block_height - (cell_size * block_size)) // 2 + offset_y
    x_offset = i * block_width + pad_x

    for y in range(block_size):
        for x in range(block_size):
            top_left = (x_offset + x * cell_size, pad_y + y * cell_size)
            bottom_right = (x_offset + (x + 1) * cell_size, pad_y + (y + 1) * cell_size)
            color = (0, 255, 0) if blocks_array[i][y][x] == 1 else (255, 0, 0)
            cv2.rectangle(visual, top_left, bottom_right, color, 1)

# --- Resize untuk Tampilan ---
display_height = int(display_width / aspect_ratio)
visual_display = cv2.resize(visual, (display_width, display_height))
binary_display = cv2.resize(binary, (display_width, display_height))

cv2.imshow("Detected Blocks", visual_display)
cv2.imshow("Binary Blocks", binary_display)
cv2.waitKey(0)
cv2.destroyAllWindows()
