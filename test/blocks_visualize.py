import pygame
import sys
import importlib.util

# Load blocks.py
spec = importlib.util.spec_from_file_location("blocks", "blocks.py")
blocks_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(blocks_module)
blocks = blocks_module.blocks

# Konfigurasi
pygame.init()
cell_size = 30
margin = 20
font = pygame.font.SysFont(None, 18)

block_size = 5 * cell_size
columns = 10
block_count = len(blocks)
rows = (block_count + columns - 1) // columns
screen_width = columns * (block_size + margin * 2) + margin
screen_height = rows * (block_size + margin * 2) + margin

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Visualisasi Semua Blok - 5 Kolom")

# Fungsi Gambar Blok
def draw_block(block_data, x_offset, y_offset, name):
    for y, row in enumerate(block_data):
        for x, cell in enumerate(row):
            rect = pygame.Rect(
                x_offset + x * cell_size,
                y_offset + y * cell_size,
                cell_size,
                cell_size
            )
            color = (255, 255, 255) if cell == 1 else (30, 30, 30)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (80, 80, 80), rect, 1)
    label = font.render(name, True, (200, 200, 200))
    screen.blit(label, (x_offset, y_offset - 18))

# Loop utama
def main():
    clock = pygame.time.Clock()
    running = True
    block_names = list(blocks.keys())
    
    while running:
        screen.fill((10, 10, 10))

        for i, name in enumerate(block_names):
            col = i % columns
            row = i // columns
            x_offset = margin + col * (block_size + margin * 2)
            y_offset = margin + row * (block_size + margin * 2)
            draw_block(blocks[name], x_offset, y_offset, name)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
