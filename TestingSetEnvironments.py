# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 12:59:31 2023

@author: gameb
"""

# from gymnasium import Env, spaces
# import numpy as np
# import itertools
from stable_baselines3 import PPO
# from stable_baselines3 import A2C
from stable_baselines3.common.env_checker import check_env
import os
from SetEnvironmentEasy import SetGameEnvEasy, SetGameEnvEasyBox


models_dir = "models/PPOEasy3"
logdir = "logsEasy3"

if not os.path.exists(models_dir):
    os.makedirs(models_dir)
if not os.path.exists(logdir):
    os.makedirs(logdir)
# os.rmdir("logs")
env = SetGameEnvEasy()
check_env(env)

env.reset()
# print("sample action:", env.action_space.sample())
# print("observation space shape", env.observation_space.shape)
# print("sample observation", env.observation_space.sample())
# model = A2C("MlpPolicy", env, verbose=1)
# model.learn(total_timesteps=100)

model = PPO("MlpPolicy", env, verbose=1, tensorboard_log=logdir)
timesteps = 10000
for i in range(1,50):
    model.learn(total_timesteps=timesteps, reset_num_timesteps=False, tb_log_name="PPO3")
    model.save(f"{models_dir}/{timesteps*i}")
# model.learn(total_timesteps=100000)








#####################################################################
models_dir = "models/PPOEasyBox"
logdir = "logsEasyBox"

if not os.path.exists(models_dir):
    os.makedirs(models_dir)
if not os.path.exists(logdir):
    os.makedirs(logdir)
# os.rmdir("logs")
env = SetGameEnvEasyBox()
check_env(env)

# os.rmdir(logdir+"/PPOBox_0")
# os.rmdir(logdir)

env.reset()
# print("sample action:", env.action_space.sample())
# print("observation space shape", env.observation_space.shape)
# print("sample observation", env.observation_space.sample())
# model = A2C("MlpPolicy", env, verbose=1)
# model.learn(total_timesteps=100)

model = PPO("MlpPolicy", env, verbose=1, tensorboard_log=logdir)
timesteps = 10000
for i in range(1,50):
    model.learn(total_timesteps=timesteps, reset_num_timesteps=False, tb_log_name="PPOBox")
    model.save(f"{models_dir}/{timesteps*i}")
    
    
model.learn(total_timesteps=1000)
