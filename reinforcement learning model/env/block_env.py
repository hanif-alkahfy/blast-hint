import numpy as np
import random
from copy import deepcopy


class Block8x8Env:
    def __init__(self, blocks_repo):
        self.grid_size = 8
        self.block_size = 5
        self.blocks_repo = blocks_repo  # dictionary dari blocks.py
        self.reset()

    def reset(self):
        self.grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.available_blocks = self._generate_blocks()
        self.done = False
        return self._get_obs()

    def _generate_blocks(self):
        return [
            {"name": name, "block": deepcopy(block)}
            for name, block in random.sample(list(self.blocks_repo.items()), 3)
        ]

    def _get_obs(self):
        return {
            "grid": deepcopy(self.grid),
            "blocks": deepcopy(self.available_blocks)
        }

    def step(self, block_index, x, y):
        if self.done:
            return self._get_obs(), -10, True, {"error": "Game over"}

        if block_index >= len(self.available_blocks):
            return self._get_obs(), 0, False, {"error": "Invalid block index"}

        block_data = self.available_blocks[block_index]
        trimmed = self._trim_block(block_data["block"])

        if not self._can_place(trimmed, x, y):
            return self._get_obs(), 0, False, {"error": "Invalid placement"}

        self._place_block(trimmed, x, y)
        lines_cleared = self._clear_full_lines()
        cells_placed = np.sum(trimmed)

        reward = cells_placed + (lines_cleared * 10) + 10  # survive bonus
        self.available_blocks.pop(block_index)

        if len(self.available_blocks) == 0:
            self.available_blocks = self._generate_blocks()

        self.done = self._check_game_over()
        return self._get_obs(), reward, self.done, {}

    def _can_place(self, block, top_x, top_y):
        for y in range(len(block)):
            for x in range(len(block[0])):
                if block[y][x] == 1:
                    gx, gy = top_x + x, top_y + y
                    if gx < 0 or gx >= self.grid_size or gy < 0 or gy >= self.grid_size:
                        return False
                    if self.grid[gy][gx] == 1:
                        return False
        return True

    def _place_block(self, block, top_x, top_y):
        for y in range(len(block)):
            for x in range(len(block[0])):
                if block[y][x] == 1:
                    self.grid[top_y + y][top_x + x] = 1

    def _clear_full_lines(self):
        rows_cleared = 0
        cols_cleared = 0

        for y in range(self.grid_size):
            if all(cell == 1 for cell in self.grid[y]):
                self.grid[y] = [0] * self.grid_size
                rows_cleared += 1

        for x in range(self.grid_size):
            if all(self.grid[y][x] == 1 for y in range(self.grid_size)):
                for y in range(self.grid_size):
                    self.grid[y][x] = 0
                cols_cleared += 1

        return rows_cleared + cols_cleared

    def _trim_block(self, block):
        min_row = min_col = self.block_size
        max_row = max_col = 0
        for y in range(self.block_size):
            for x in range(self.block_size):
                if block[y][x] == 1:
                    min_row = min(min_row, y)
                    max_row = max(max_row, y)
                    min_col = min(min_col, x)
                    max_col = max(max_col, x)
        trimmed = []
        for y in range(min_row, max_row + 1):
            trimmed.append(block[y][min_col:max_col + 1])
        return trimmed

    def _check_game_over(self):
        for i, b in enumerate(self.available_blocks):
            block = self._trim_block(b["block"])
            for y in range(self.grid_size - len(block) + 1):
                for x in range(self.grid_size - len(block[0]) + 1):
                    if self._can_place(block, x, y):
                        return False
        return True

    def get_state_vector(self):
        grid_flat = np.array(self.grid).flatten()

        blocks_flat = []
        for b in self.available_blocks:
            block_arr = np.array(b["block"]).flatten()
            blocks_flat.extend(block_arr)

        # Jika jumlah blok < 3 → padding
        while len(blocks_flat) < 3 * 25:
            blocks_flat.extend([0] * 25)

        return np.concatenate([grid_flat, np.array(blocks_flat)])