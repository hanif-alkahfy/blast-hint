# test/test_pipeline.py
import sys
import os
import cv2
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from extractors.pipeline import extract_game_state
from vis.visualizer import visualize_grid_and_blocks

img = cv2.imread('./assets/test_image_10.png')
game_state = extract_game_state(img)
visualize_grid_and_blocks(game_state["grid"], game_state["blocks"])
