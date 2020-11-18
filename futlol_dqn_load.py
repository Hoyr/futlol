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

"""DQN agents trained on Futlol by independent Q-learning."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import os
import random
import gc

from absl import app
from absl import flags
from absl import logging
import numpy as np
import tensorflow.compat.v1 as tf
import pyspiel

from open_spiel.python.utils import file_logger
from open_spiel.python import rl_environment
from open_spiel.python.algorithms import dqn
from open_spiel.python.algorithms import random_agent

FLAGS = flags.FLAGS

# Training parameters
flags.DEFINE_string("checkpoint_dir", "./futlol_dqn/",
                    "Directory to save/load the agent.")
flags.DEFINE_integer("num_train_episodes", int(1e6),
                     "Number of training episodes.")
flags.DEFINE_integer(
    "eval_every", 10,
    "Episode frequency at which the DQN agents are evaluated.")
flags.DEFINE_integer(
    "num_eval_games", 100,
    "How many games to play during each evaluation.")
flags.DEFINE_bool("load_last", True,
                  "Load a last saved agent.")
flags.DEFINE_integer(
    "start_ep", 0,
    "What episode number to start on.")

# DQN model hyper-parameters
flags.DEFINE_list("hidden_layers_sizes", [64, 64],
                  "Number of hidden units in the Q-Network MLP.")
flags.DEFINE_integer("replay_buffer_capacity", int(1e4),
                     "Size of the replay buffer.")
flags.DEFINE_integer("batch_size", 32,
                     "Number of transitions to sample at each learning step.")
flags.DEFINE_bool("randomize_positions", False,
                  "Randomize the position of each agent before every game.")

# def eval_against_random_bots(env, trained_agents, random_agents, num_episodes):
#   """Evaluates `trained_agents` against `random_agents` for `num_episodes`."""
#   num_players = len(trained_agents)
#   sum_episode_rewards = np.zeros(num_players)
#   for test_team in range(2):
#     for _ in range(num_episodes):
#       cur_agents = random_agents[:]
#       episode_rewards = np.zeros(num_players)
#       for i in range(num_players):
#         if i%2==test_team:
#           cur_agents[i] = trained_agents[i]
#       time_step = env.reset()
      
#       while not time_step.last():
#         player_id = time_step.observations["current_player"]
#         agent_output = cur_agents[player_id].step(
#             time_step, is_evaluation=True)
#         action_list = [agent_output.action]
#         time_step = env.step(action_list)
#         for i in range(num_players):
#           if i%2==test_team:
#             episode_rewards[i] += time_step.rewards[i]
#       sum_episode_rewards += episode_rewards
#   return sum_episode_rewards / num_episodes

def main(_):
  game = "futlol"
  num_players = 6
  num_players_per_team=int(num_players/2)
  num_teams = 6

  logger=file_logger.FileLogger(os.path.join(FLAGS.checkpoint_dir, "game_stats"),"Game_Stats[{}]".format(datetime.datetime.now().isoformat(" ")))
  maxSelfRatioTeam = [1.0, 0.0, #0
                      1.0, 0.0,
                      1.0, 0.0,
                      1.0, 0.0,
                      1.0, 0.0,
                      1.0, 0.0,
                      1.0, 0.0,
                      1.0, 0.0,
                      False]
  twiceSelfRatioTeam = [1.0, 0.5, #1
                      1.0, 0.5,
                      1.0, 0.5,
                      1.0, 0.5,
                      1.0, 0.5,
                      1.0, 0.5,
                      1.0, 0.5,
                      1.0, 0.5,
                      False]
  equalSelfRatioTeam = [1.0, 1.0, #2
                      1.0, 1.0,
                      1.0, 1.0,
                      1.0, 1.0,
                      1.0, 1.0,
                      1.0, 1.0,
                      1.0, 1.0,
                      1.0, 1.0,
                      False]
  halfSelfRatioTeam = [0.5, 1.0, #3
                      0.5, 1.0,
                      0.5, 1.0,
                      0.5, 1.0,
                      0.5, 1.0,
                      0.5, 1.0,
                      0.5, 1.0,
                      0.5, 1.0,
                      False]
  zeroSelfRatioTeam = [0.0, 1.0, #4
                      0.0, 1.0,
                      0.0, 1.0,
                      0.0, 1.0,
                      0.0, 1.0,
                      0.0, 1.0,
                      0.0, 1.0,
                      0.0, 1.0,
                      False]
  winOnlyRatioTeam = [0.0, 1.0, #5
                      0.0, 1.0,
                      0.0, 1.0,
                      0.0, 1.0,
                      0.0, 1.0,
                      0.0, 1.0,
                      0.0, 1.0,
                      0.0, 1.0,
                      True]
  TeamArgs = [maxSelfRatioTeam, twiceSelfRatioTeam, equalSelfRatioTeam, halfSelfRatioTeam, zeroSelfRatioTeam, winOnlyRatioTeam]

  #env_configs = {}
  #env = rl_environment.Environment(game, **env_configs)
  envs={}
  for team1 in range(0,num_teams):
    for team2 in range(team1,num_teams):
      game_settings = {}
      for k in range(8):
        game_settings["P"+str(2*k)+"Self"]=TeamArgs[team1][2*k]
        game_settings["P"+str(2*k)+"Team"]=TeamArgs[team1][2*k+1]
        game_settings["P"+str(2*k+1)+"Self"]=TeamArgs[team2][2*k]
        game_settings["P"+str(2*k+1)+"Team"]=TeamArgs[team2][2*k+1]
      game_settings["EvenWinOnly"]=TeamArgs[team1][16]
      game_settings["OddWinOnly"]=TeamArgs[team2][16]
      envs[str(team1)+str(team2)] = rl_environment.Environment(game, **game_settings)
  
  observation_tensor_size = envs[str(0)+str(0)].observation_spec()["info_state"][0]
  num_actions = envs[str(0)+str(0)].action_spec()["num_actions"]

  with tf.Session() as sess:
    #summaries_dir = os.path.join(FLAGS.checkpoint_dir, "rreval")
    #summary_writer = tf.summary.FileWriter(summaries_dir, tf.get_default_graph())
    hidden_layers_sizes = [int(l) for l in FLAGS.hidden_layers_sizes]

    agents = [
        dqn.DQN(
            session=sess,
            player_id=idx,
            state_representation_size=observation_tensor_size,
            num_actions=num_actions,
            hidden_layers_sizes=hidden_layers_sizes,
            replay_buffer_capacity=FLAGS.replay_buffer_capacity,
            batch_size=FLAGS.batch_size) for idx in range(num_players_per_team*num_teams)
    ]

    saver = tf.train.Saver(max_to_keep=0)
    if FLAGS.load_last:
      saver.restore(sess, tf.train.latest_checkpoint(FLAGS.checkpoint_dir))
    else:
      sess.run(tf.global_variables_initializer())

    player_map=[0,1,2,3,4,5]
    round_rewards = [0 for i in range(num_players)]
    for ep in range(FLAGS.start_ep, FLAGS.num_train_episodes):
      for team1 in range(0,num_teams):
        for team2 in range(team1,num_teams):
          print("Ep: "+str(ep)+" "+str(team1)+" vs "+str(team2)+" "+str(datetime.datetime.now().isoformat(" "))+"\r",end="")

          for k in range(3):
            player_map[2*k]=team1*num_players_per_team+k
            player_map[2*k+1]=team2*num_players_per_team+k

          time_step = envs[str(team1)+str(team2)].reset()
          
          if (ep + 1) % FLAGS.eval_every == 0:
            gamelogger=file_logger.FileLogger(os.path.join(FLAGS.checkpoint_dir, "game_stats"),"Game_Log_{}v{}ep{}[{}]".format(team1,team2,ep+1,datetime.datetime.now().isoformat(" ")))
            for k in range(len(round_rewards)):
               round_rewards[k] = 0

          while not time_step.last():
            player_id = time_step.observations["current_player"]
            position = player_map[player_id]
            agents[position].player_id = player_id
            time_step = envs[str(team1)+str(team2)].step([agents[position].step(time_step).action])
            if (ep + 1) % FLAGS.eval_every == 0:
              gamelogger.print(str(envs[str(team1)+str(team2)]._state))
              for i in range(num_players):
                round_rewards[i] += time_step.rewards[i]
          logger.print(str(ep+1)+", "+str(team1)+", "+str(team2)+", "+str(envs[str(team1)+str(team2)]._state).splitlines()[0])
            
          # Episode is over, step all agents with final info state.
          for agent in agents:
            agent.step(time_step)

          time_step = envs[str(team1)+str(team2)].reset()
          
          if (ep + 1) % FLAGS.eval_every == 0:
            gamelogger.close()
            logging.info("[%s] Team %s vs %s rewards %s", ep + 1, team1, team2, round_rewards)
            #for k in range(num_players):
            #  summary = tf.Summary()
            #  summary.value.add(tag="round_reward_{}_{}_vs_{}".format(player_map[k],team1,team2),
            #                    simple_value=round_rewards[k])
            #  summary_writer.add_summary(summary, ep)
            #summary_writer.flush()
      if (ep + 1) % FLAGS.eval_every == 0:
        saver.save(sess, FLAGS.checkpoint_dir+"futlol-dqn", ep+1)
    logger.close()


if __name__ == "__main__":
  app.run(main)
