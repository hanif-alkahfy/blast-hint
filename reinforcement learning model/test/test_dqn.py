import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import torch
from env.block_env import Block8x8Env
from agents.dqn_agent import DQNAgent
from blocks import blocks
import numpy as np
from utils.encoder import decode_action


MODEL_PATH = "models/dqn_model.pth"

def test():
    env = Block8x8Env(blocks)
    state_dim = 64 + 75  # 8x8 grid + 3 blocks (5x5)
    action_dim = 3 * 64  # 3 blocks * 64 positions
    agent = DQNAgent(state_dim, action_dim)

    # Load model
    agent.model.load_state_dict(torch.load(MODEL_PATH))
    agent.model.eval()
    print("✅ Model loaded!")

    obs = env.reset()
    state = env.get_state_vector()
    done = False
    total_reward = 0
    step = 0

    while not done:
        action_index = agent.select_action(state, explore=False)  # disable exploration
        block_idx, x, y = decode_action(action_index)

        obs, reward, done, info = env.step(block_idx, x, y)
        next_state = env.get_state_vector()

        print(f"Step {step}: Place block {block_idx} at ({x},{y}) → reward={reward}")
        state = next_state
        total_reward += reward
        step += 1

    print(f"\n🎉 Total Steps: {step}")
    print(f"🏆 Total Reward: {total_reward}")

if __name__ == "__main__":
    test()
