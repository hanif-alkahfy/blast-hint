import matplotlib.pyplot as plt
import numpy as np
import random
from .blocks import blocks as known_blocks  # blocks.py harus berada di 1 folder yg sama

def trim_block(block):
    block = np.array(block)
    rows = np.any(block, axis=1)
    cols = np.any(block, axis=0)
    return block[np.ix_(rows, cols)]

def match_block_name(trimmed_block):
    for name, known in known_blocks.items():
        if np.array_equal(trimmed_block, trim_block(known)):
            return name
    return "Unknown"

def visualize_grid_and_blocks(grid, blocks, fig=None):
    pastel_colors = ["#AEDFF7", "#F9C0D9", "#D4F5A3", "#FFF2AE", "#D6C8F1", "#FFDAC1"]
    empty_color = "#E0E0E0"

    if fig is None:
        fig = plt.figure(figsize=(4, 5))
    fig.clf()  # Hapus isi figure lama

    fig.patch.set_facecolor('#f9f9f9')

    def draw_grid(ax, data, color_map, show_grid=True, mask=None):
        ax.imshow(data, cmap=color_map, vmin=0, vmax=np.max(data), extent=[0, data.shape[1], data.shape[0], 0])

        ax.set_xticks(np.arange(0, data.shape[1] + 1, 1))
        ax.set_yticks(np.arange(0, data.shape[0] + 1, 1))

        if show_grid:
            for y in range(data.shape[0]):
                for x in range(data.shape[1]):
                    if mask is None or mask[y, x]:
                        ax.plot([x, x + 1], [y, y], color='black', linewidth=0.5)       # Top
                        ax.plot([x, x + 1], [y + 1, y + 1], color='black', linewidth=0.5) # Bottom
                        ax.plot([x, x], [y, y + 1], color='black', linewidth=0.5)       # Left
                        ax.plot([x + 1, x + 1], [y, y + 1], color='black', linewidth=0.5) # Right

        ax.set_aspect('equal')
        ax.tick_params(which='both', bottom=False, left=False, labelbottom=False, labelleft=False)



    # ----- Subplot Grid 8x8 (atas) -----
    ax1 = fig.add_subplot(2, 1, 1)
    grid_color = random.choice(pastel_colors)
    grid_cmap = plt.cm.colors.ListedColormap([empty_color, grid_color])
    draw_grid(ax1, grid, grid_cmap, show_grid=True)
    ax1.set_title("8x8 Grid")

    # ----- Subplot Blocks (bawah) -----
    ax2 = fig.add_subplot(2, 1, 2)
    container = np.zeros((7, 21), dtype=np.uint8)
    block_cmap = plt.cm.colors.ListedColormap(['white'] + pastel_colors)

    for i, blk in enumerate(blocks[:3]):
        color_idx = i + 1
        block = np.array(blk)
        trimmed = trim_block(block)
        h, w = trimmed.shape

        start_x = i * 7 + 1
        start_y = (7 - h) // 2
        start_x_offset = start_x + (5 - w) // 2
        container[start_y:start_y + h, start_x_offset:start_x_offset + w] = trimmed * color_idx

        name = match_block_name(trimmed)
        ax2.text(start_x + 2.5, -0.5, name, ha='center', va='bottom', fontsize=8, color='black')

    draw_grid(ax2, container, block_cmap, show_grid=True, mask=(container > 0))

    plt.tight_layout()
    fig.canvas.draw()              # << refresh isi figure
    fig.canvas.flush_events()      # << update window segera
