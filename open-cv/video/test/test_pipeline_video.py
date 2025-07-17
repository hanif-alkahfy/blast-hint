# test/test_pipeline_video.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
import matplotlib.pyplot as plt
from extractors.pipeline import extract_game_state
from vis.visualizer import visualize_grid_and_blocks

# === Path video ===
VIDEO_PATH = 'assets/test_video.mp4'

# === Buka video ===
cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print("Gagal membuka video.")
    exit()

# Loop per frame
while True:
    ret, frame = cap.read()
    if not ret:
        break  # video habis

    try:
        # Ekstraksi dari frame
        result = extract_game_state(frame)

        # Visualisasi hasil
        visualize_grid_and_blocks(result['grid'], result['blocks'])
    
    except Exception as e:
        print(f"Error pada frame: {e}")
        continue  # lanjut ke frame berikutnya

    # Tunggu sebentar sebelum tampilkan frame selanjutnya
    plt.pause(0.001)  # jeda kecil untuk real-time feel

# Tutup video
cap.release()
