# extractors/block_extractor.py

import cv2
import numpy as np

def trim_block(block):
    """
    Memotong blok 5x5 untuk menghilangkan area kosong di luar bentuk blok.

    Args:
        block (np.ndarray): Array 2D berisi 0 dan 1 (ukuran 5x5)

    Returns:
        np.ndarray: Array yang sudah dipotong (ukuran <= 5x5)
    """
    block = np.array(block)  # Pastikan dalam format np.ndarray
    rows = np.any(block, axis=1)
    cols = np.any(block, axis=0)

    if not rows.any() or not cols.any():
        return np.zeros((1, 1), dtype=np.uint8)

    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]

    return block[rmin:rmax+1, cmin:cmax+1]

def extract_blocks(img):
    """
    Mengekstrak 3 blok berukuran 5x5 dari screenshot game.

    Args:
        img (np.ndarray): Gambar screenshot game (BGR atau RGB)

    Returns:
        list of np.ndarray: List berisi 3 blok shape (5,5)
    """

    block_count = 3
    block_size = 5
    block_crop_coords = (230, 1670, 1400, 2170)
    target_block_height = 400
    manual_scale = 0.85
    offset_correction_x = 4
    offset_correction_y = 4

    x1, y1, x2, y2 = block_crop_coords
    cropped = img[y1:y2, x1:x2]

    crop_h, crop_w = cropped.shape[:2]
    aspect_ratio = crop_w / crop_h
    resize_width = int(target_block_height * aspect_ratio)
    resized = cv2.resize(cropped, (resize_width, target_block_height))

    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV, 11, 3)

    block_width = resize_width // block_count
    cell_size = int((min(block_width, target_block_height) // block_size) * manual_scale)

    blocks_array = []

    for i in range(block_count):
        x_start = i * block_width
        x_end = x_start + block_width
        roi = binary[:, x_start:x_end]

        contours, _ = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            blocks_array.append(np.zeros((block_size, block_size), dtype=np.uint8))
            continue

        largest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest)

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
        trimmed_block = trim_block(np.array(block_matrix, dtype=np.uint8))
        blocks_array.append(trimmed_block)

    return blocks_array