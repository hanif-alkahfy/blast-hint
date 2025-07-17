# extractors/grid_extractor.py

import cv2
import numpy as np

def extract_grid(img):
    """
    Mengekstrak grid 8x8 dari screenshot game.

    Args:
        img (np.ndarray): Gambar screenshot game (BGR atau RGB)

    Returns:
        np.ndarray: Matriks 8x8 (isi 0 dan 1)
    """
    grid_size = 8
    resize_dim = 512
    crop_coords = (230, 420, 1400, 1600)  # Disesuaikan agar pas dengan area grid

    x1, y1, x2, y2 = crop_coords
    cropped = img[y1:y2, x1:x2]
    img_resized = cv2.resize(cropped, (resize_dim, resize_dim))
    gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)

    binary = cv2.adaptiveThreshold(gray, 255,
                                   cv2.ADAPTIVE_THRESH_MEAN_C,
                                   cv2.THRESH_BINARY_INV,
                                   11, 3)

    cell_size = resize_dim // grid_size
    grid = []

    for y in range(grid_size):
        row = []
        for x in range(grid_size):
            pad = int(cell_size * 0.2)
            x_start = x * cell_size + pad
            y_start = y * cell_size + pad
            x_end = (x + 1) * cell_size - pad
            y_end = (y + 1) * cell_size - pad

            cell = binary[y_start:y_end, x_start:x_end]
            nonzero_count = cv2.countNonZero(cell)
            total_pixels = cell.shape[0] * cell.shape[1]

            filled_ratio = nonzero_count / total_pixels
            value = 1 if filled_ratio > 0.1 else 0  # Threshold bisa disesuaikan
            row.append(value)
        grid.append(row)

    return np.array(grid, dtype=np.uint8)
