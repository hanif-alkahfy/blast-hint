import numpy as np
from .grid_extractor import extract_grid
from .block_extractor import extract_blocks

def extract_game_state(img):
    """
    Menggabungkan ekstraksi grid 8x8 dan tiga blok 5x5 dari gambar screenshot.

    Args:
        img (np.ndarray): Screenshot dari game, format BGR atau RGB.

    Returns:
        dict: {
            "grid": np.ndarray shape (8, 8),
            "blocks": [np.ndarray shape (5,5), np.ndarray shape (5,5), np.ndarray shape (5,5)]
        }
    """
    # Ekstraksi grid dari gambar
    grid_8x8 = extract_grid(img)
    
    # Ekstraksi tiga blok 5x5 dari gambar
    block_list_5x5 = extract_blocks(img)

    # Validasi bentuk hasil
    if grid_8x8.shape != (8, 8):
        raise ValueError(f"Grid shape mismatch: expected (8,8), got {grid_8x8.shape}")
    
    if len(block_list_5x5) != 3:
        raise ValueError(f"Expected 3 blocks, got {len(block_list_5x5)}")

    for i, blk in enumerate(block_list_5x5):
        if blk.shape[0] > 5 or blk.shape[1] > 5:
            raise ValueError(f"Block {i} shape too big: got {blk.shape}")


    return {
        "grid": grid_8x8,
        "blocks": block_list_5x5
    }
