from env.block_env import Block8x8Env
from blocks import blocks
import numpy as np


def print_grid(grid):
    for row in grid:
        print(" ".join(str(cell) for cell in row))


def print_blocks(block_list):
    for i, b in enumerate(block_list):
        print(f"Block {i} ({b['name']}):")
        for row in b["block"]:
            print(" ".join(str(cell) for cell in row))
        print()


def main():
    env = Block8x8Env(blocks)
    obs = env.reset()
    done = False
    total_reward = 0
    step = 0

    while not done:
        print(f"\nStep {step}")
        print("Grid:")
        print_grid(obs["grid"])

        print("\nAvailable Blocks:")
        print_blocks(obs["blocks"])

        try:
            user_input = input("Enter action (block_index x y): ")
            if user_input.strip().lower() in ["q", "quit", "exit"]:
                break
            bi, x, y = map(int, user_input.strip().split())
            obs, reward, done, info = env.step(bi, x, y)

            print(f"\nReward: {reward}")
            if info:
                print(f"Info: {info}")

            total_reward += reward
            step += 1
        except Exception as e:
            print(f"Error: {e}")

    print("\n=== Game Over ===")
    print("Final Grid:")
    print_grid(obs["grid"])
    print(f"Total Reward: {total_reward}")


if __name__ == "__main__":
    main()
