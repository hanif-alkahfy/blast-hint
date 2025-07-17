# train/train_dqn.py
import os
import numpy as np
import torch
from env.block_env import Block8x8Env
from blocks import blocks
from agents.dqn_agent import DQNAgent
from utils.encoder import encode_action, decode_action


SAVE_PATH = "models/dqn_model.pth"
EPISODES = 100
TARGET_UPDATE_FREQ = 10


def train():
    env = Block8x8Env(blocks)
    state_dim = 64 + 75  # 8x8 grid + 3 blocks (5x5)
    action_dim = 3 * 64  # 3 block index × 64 positions (8x8)
    agent = DQNAgent(state_dim, action_dim)

    reward_history = []
    step_history = []

    for episode in range(EPISODES):
        obs = env.reset()
        state = env.get_state_vector()
        total_reward = 0
        done = False
        step = 0

        while not done:
            action_index = agent.select_action(state)
            block_index, x, y = decode_action(action_index)
            next_obs, reward, done, info = env.step(block_index, x, y)

            next_state = env.get_state_vector()
            agent.store_transition(state, action_index, reward, next_state, done)

            agent.train_step()
            state = next_state
            total_reward += reward
            step += 1

        reward_history.append(total_reward)
        step_history.append(step)
        agent.decay_epsilon()

        if episode % TARGET_UPDATE_FREQ == 0:
            agent.update_target_network()

        print(f"Episode {episode} | Steps: {step} | Total Reward: {total_reward:.1f} | Epsilon: {agent.epsilon:.3f}")

    torch.save(agent.model.state_dict(), SAVE_PATH)
    print(f"Model saved to {SAVE_PATH}")


if __name__ == "__main__":
    os.makedirs("models", exist_ok=True)
    train()