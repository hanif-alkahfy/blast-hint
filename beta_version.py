import importlib.util
import random
import pygame
import itertools
import sys

# Load blocks.py
spec = importlib.util.spec_from_file_location("blocks", "blocks.py")
blocks_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(blocks_module)
blocks = blocks_module.blocks

# Konfigurasi pygame
pygame.init()
cell_size = 40
grid_size = 8
block_size = 5
margin = 10

game_over = False
font = pygame.font.SysFont(None, 72)

# Lebar minimum agar 3 blok muat di bawah
screen_width = max(grid_size * cell_size + 3 * margin, 3 * (block_size * cell_size) + margin + 100)
grid_width = grid_size * cell_size + 2 * margin
screen_height = grid_size * cell_size + (block_size * cell_size) + 4 * margin + 50
screen = pygame.display.set_mode((screen_width, screen_height))
grid_offset_x = (screen_width - grid_width) // 2

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Block Drag & Drop to 8x8 Grid")

# Grid kosong 8x8
grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]

# Fungsi untuk menghasilkan warna pastel acak
def random_pastel_color():
    base = 200
    return (
        random.randint(base, 255),
        random.randint(base, 255),
        random.randint(base, 255)
    )

# Inisialisasi 3 block pertama
def generate_blocks():
    new_blocks = []
    total_width = 3 * (block_size * cell_size) + 2 * 20  # 3 blok + 2 celah
    start_x = (screen_width - total_width) // 2
    y = grid_size * cell_size + 2 * margin + 50

    for i, (name, block) in enumerate(random.sample(list(blocks.items()), 3)):
        x = start_x + i * (block_size * cell_size + 50)
        new_blocks.append({
            "name": name,
            "block": block,
            "pos": (x, y),
            "color": random_pastel_color()
        })
    return new_blocks

available_blocks = generate_blocks()

# --- Fungsi Utilitas ---

def draw_grid():
    for y in range(grid_size):
        for x in range(grid_size):
            rect = pygame.Rect(
                grid_offset_x + x * cell_size,
                margin + y * cell_size,
                cell_size,
                cell_size
            )
            color = (200, 200, 200) if grid[y][x] == 0 else (100, 200, 255)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (50, 50, 50), rect, 1)

def draw_block(block, offset_x, offset_y, color=(255, 255, 255)):
    for y in range(len(block)):
        for x in range(len(block[0])):
            if block[y][x] == 1:
                rect = pygame.Rect(offset_x + x * cell_size, offset_y + y * cell_size, cell_size, cell_size)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (50, 50, 50), rect, 1)

def can_place_block(grid, block, top_x, top_y):
    for y in range(len(block)):
        for x in range(len(block[0])):
            if block[y][x] == 1:
                gx = top_x + x
                gy = top_y + y
                if gx < 0 or gx >= grid_size or gy < 0 or gy >= grid_size:
                    return False
                if grid[gy][gx] == 1:
                    return False
    return True

def place_block(grid, block, top_x, top_y):
    for y in range(len(block)):
        for x in range(len(block[0])):
            if block[y][x] == 1:
                grid[top_y + y][top_x + x] = 1

def clear_full_lines(grid):
    for y in range(grid_size):
        if all(cell == 1 for cell in grid[y]):
            grid[y] = [0] * grid_size
    for x in range(grid_size):
        if all(grid[y][x] == 1 for y in range(grid_size)):
            for y in range(grid_size):
                grid[y][x] = 0

def trim_block(block):
    min_row = min_col = 5
    max_row = max_col = 0

    for y in range(5):
        for x in range(5):
            if block[y][x] == 1:
                min_row = min(min_row, y)
                max_row = max(max_row, y)
                min_col = min(min_col, x)
                max_col = max(max_col, x)

    trimmed = []
    for y in range(min_row, max_row + 1):
        trimmed.append(block[y][min_col:max_col + 1])
    return trimmed

def is_game_over(grid, blocks):
    print("=== CEK GAME OVER ===")
    for i, b in enumerate(blocks):
        block = trim_block(b["block"])
        print(f"Blok ke-{i}:")
        for row in block:
            print(row)

        found_place = False
        for y in range(grid_size - len(block) + 1):
            for x in range(grid_size - len(block[0]) + 1):
                if can_place_block(grid, block, x, y):
                    print(f"→ BISA diletakkan di posisi ({x}, {y})")
                    found_place = True
                    break
            if found_place:
                break

        if found_place:
            print(f"✅ Blok ke-{i} MASIH BISA dipakai.")
            return False

        else:
            print(f"❌ Blok ke-{i} TIDAK BISA ditempatkan.")

    print("💀 SEMUA BLOK TIDAK BISA DIPAKAI → GAME OVER")
    return True

restart_font = pygame.font.SysFont(None, 36)
restart_button_rect = pygame.Rect(screen_width // 2 - 80, screen_height // 2 + 60, 160, 50)

def reset_game():
    global grid, available_blocks, game_over
    grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
    available_blocks = generate_blocks()
    game_over = False

# --- Game State ---
dragging = False
dragged_block = None
drag_offset = (0, 0)
running = True
clock = pygame.time.Clock()

# --- Loop Utama ---
while running:
    screen.fill((30, 30, 30))
    draw_grid()

    # Gambar blok yang tersedia
    for i, b in enumerate(available_blocks):
        if not dragging or dragged_block != i:
            draw_block(b["block"], b["pos"][0], b["pos"][1], b["color"])

    # Gambar blok yang sedang di-drag
    if dragging and dragged_block is not None:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        offset_x = mouse_x - drag_offset[0]
        offset_y = mouse_y - drag_offset[1]
        draw_block(available_blocks[dragged_block]["block"], offset_x, offset_y, available_blocks[dragged_block]["color"])

    # Tampilkan teks GAME OVER
    if game_over:
        text = font.render("GAME OVER", True, (255, 100, 100))
        text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.blit(text, text_rect)

        pygame.draw.rect(screen, (70, 180, 70), restart_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), restart_button_rect, 2)
        restart_text = restart_font.render("Restart", True, (255, 255, 255))
        restart_text_rect = restart_text.get_rect(center=restart_button_rect.center)
        screen.blit(restart_text, restart_text_rect)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # Jika game over → cek klik tombol restart
            if game_over:
                if restart_button_rect.collidepoint((mx, my)):
                    reset_game()
                continue

            # Jika tidak game over → proses drag block
            for i, b in enumerate(available_blocks):
                bx, by = b["pos"]
                block_rect = pygame.Rect(bx, by, block_size * cell_size, block_size * cell_size)
                if block_rect.collidepoint(mx, my):
                    dragging = True
                    dragged_block = i
                    drag_offset = (mx - bx, my - by)
                    break


        elif event.type == pygame.MOUSEBUTTONUP and not game_over:
            if dragging and dragged_block is not None:
                mx, my = event.pos
                offset_x = mx - drag_offset[0]
                offset_y = my - drag_offset[1]

                grid_x = (offset_x - grid_offset_x + cell_size // 2) // cell_size
                grid_y = (offset_y - margin + cell_size // 2) // cell_size

                block = available_blocks[dragged_block]["block"]
                if can_place_block(grid, block, grid_x, grid_y):
                    trimmed = trim_block(block)
                    place_block(grid, trimmed, grid_x, grid_y)
                    available_blocks.pop(dragged_block)
                    clear_full_lines(grid)

                    dragging = False
                    dragged_block = None

                    # 🔄 Jika masih ada blok tersisa → cek game over
                    if len(available_blocks) > 0:
                        if is_game_over(grid, available_blocks):
                            game_over = True

                    # 🔄 Jika semua blok sudah habis → refill dan cek game over
                    elif len(available_blocks) == 0:
                        available_blocks = generate_blocks()

                        if is_game_over(grid, available_blocks):
                            game_over = True

            # Jika semua blok sudah habis
            if not game_over and len(available_blocks) == 0:
                available_blocks = generate_blocks()

                if is_game_over(grid, available_blocks):
                    game_over = True

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
