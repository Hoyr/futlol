# Copyright 2019 DeepMind Technologies Ltd. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""DQN agents trained on Skat by independent Q-learning."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import random
import curses
import time

from absl import app
from absl import flags
from absl import logging
import numpy as np
import tensorflow.compat.v1 as tf

from open_spiel.python import rl_environment
from open_spiel.python.algorithms import dqn
from open_spiel.python.algorithms import random_agent

FLAGS = flags.FLAGS

# Training parameters
flags.DEFINE_string("checkpoint_dir", "/tmp/futlol_dqn/",
                    "Directory to save/load the agent.")
flags.DEFINE_integer("num_train_episodes", int(1e5),
                     "Number of training episodes.")
flags.DEFINE_integer(
    "eval_every", 100,
    "Episode frequency at which the DQN agents are evaluated.")
flags.DEFINE_integer(
    "num_eval_games", 100,
    "How many games to play during each evaluation.")
flags.DEFINE_bool("load_last", True,
                  "Load an last saved agent.")

# DQN model hyper-parameters
flags.DEFINE_list("hidden_layers_sizes", [64, 64],
                  "Number of hidden units in the Q-Network MLP.")
flags.DEFINE_integer("replay_buffer_capacity", int(1e4),
                     "Size of the replay buffer.")
flags.DEFINE_integer("batch_size", 32,
                     "Number of transitions to sample at each learning step.")
flags.DEFINE_bool("randomize_positions", True,
                  "Randomize the position of each agent before every game.")

def eval_against_random_bots(env, trained_agents, random_agents, num_episodes):
  """Evaluates `trained_agents` against `random_agents` for `num_episodes`."""
  num_players = len(trained_agents)
  sum_episode_rewards = np.zeros(num_players)
  for player_pos in range(num_players):
    for _ in range(num_episodes):
      cur_agents = random_agents[:]
      if FLAGS.randomize_positions:
        eval_player_pos = random.randrange(num_players)
      else:
        eval_player_pos = player_pos
      cur_agents[eval_player_pos] = trained_agents[player_pos]
      cur_agents[eval_player_pos].player_id = eval_player_pos
      time_step = env.reset()
      episode_rewards = 0
      while not time_step.last():
        player_id = time_step.observations["current_player"]
        agent_output = cur_agents[player_id].step(
            time_step, is_evaluation=True)
        action_list = [agent_output.action]
        time_step = env.step(action_list)
        episode_rewards += time_step.rewards[eval_player_pos]
      sum_episode_rewards[player_pos] += episode_rewards
  return sum_episode_rewards / num_episodes

def main(_):
  game = "futlol"
  num_players = 6

  env_configs = {}
  env = rl_environment.Environment(game, **env_configs)
  observation_tensor_size = env.observation_spec()["info_state"][0]
  num_actions = env.action_spec()["num_actions"]

  # random agents for evaluation

  with tf.Session() as sess:
    hidden_layers_sizes = [int(l) for l in FLAGS.hidden_layers_sizes]

    # pylint: disable=g-complex-comprehension
    agents = [
        dqn.DQN(
            session=sess,
            player_id=idx,
            state_representation_size=observation_tensor_size,
            num_actions=num_actions,
            hidden_layers_sizes=hidden_layers_sizes,
            replay_buffer_capacity=FLAGS.replay_buffer_capacity,
            batch_size=FLAGS.batch_size) for idx in range(num_players)
    ]

    saver = tf.train.Saver()
    if FLAGS.load_last:
      saver.restore(sess, tf.train.latest_checkpoint(FLAGS.checkpoint_dir))
    else:
      sess.run(tf.global_variables_initializer())

    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()

    time_step = env.reset()
    try:
      stdscr.addstr(1, 0, str(env._state))
      stdscr.refresh()
      stdscr.getch()
      # Randomize position.
      while not time_step.last():
        player_id = time_step.observations["current_player"]
        agent_output = agents[player_id].step(time_step)
        action_list = [agent_output.action]
        time_step = env.step(action_list)
        stdscr.addstr(0, 0, env._state.action_to_string(player_id, agent_output.action))
        stdscr.clrtoeol()
        stdscr.addstr(1, 0, str(env._state))
        stdscr.refresh()
        time.sleep(0.5)

      stdscr.addstr(0, 0, env._state.action_to_string(player_id, agent_output.action))
      stdscr.clrtoeol()
      stdscr.addstr(1, 0, str(env._state))
      stdscr.refresh()
      stdscr.getch()

    finally:
      curses.echo()
      curses.nocbreak()
      curses.endwin()


if __name__ == "__main__":
  app.run(main)
