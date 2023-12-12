# -*- coding: utf-8 -*-
"""
Created on Sat Dec  9 00:13:33 2023

@author: gameb
"""
# import gymnasium as gym
from gymnasium import Env, spaces
import numpy as np
import itertools
from stable_baselines3 import PPO, A2C
from stable_baselines3.common.env_checker import check_env
import os

class SetGameEnv(Env):
    def __init__(self):
        """
        Creates the space needed, and some others for testing
        Needs the observation_space and action_space
        """
        super(SetGameEnv, self).__init__()
        #For checking runs
        self.reset_count=0
        self.all_runs = []
        
        ############################# For the game portion
        self.deck = np.array([])
        self.board = np.array([])
        #this is for checking sets
        # print(self.board)
        self.cardvalues = self.gen_card_vals()
        self.cardcombos = [] #used in other functions (check board)
        #############################
        
        # #Make a list of all possible combinations of 3 cards of 12
        # choices = np.array(list(itertools.combinations(np.arange(12),3)))
        # self.actions = [0]+choices #add option for saying no set on board
        
        # self.rng = default_rng()
        
        self.score = 0 #initialize score at 0
        # self.current_obs = None 
        # self.output_shape = (12,12,12)
        # self.action_space = spaces.MultiDiscrete((12,12,12))
        temp_deck = np.arange(12)
        self.action_options = [list(tup) for tup in itertools.combinations(temp_deck, 3)]
        self.action_space = spaces.Discrete(220)
        
        
        self.observation_space = spaces.Box(
            low=1,
            high=81,
            shape=(12,), 
            dtype=np.uint8)
    
    def reset(self, seed=0):
    # def reset(self):
        """
        Returns: the observation of the initial state
        -------
        Resets the environment to initial state so a new episode can start
        The new episodes should be independent from previous ones
        """
        self.done = False
        self.deck = np.arange(1,82).astype(np.uint8)
        self.board = np.array([])
        #shuffle it 
        np.random.shuffle(self.deck)
        #Add 12 of the cards to the board
        # print("DEBUG: no cards should be here:", self.board)
        self.add_cards(12)
        # print("board:",self.board)
        set_on_board = False
        stop_loop = 0
        while not set_on_board and stop_loop<100:
            stop_loop += 1
            #check board for set
            set_on_board = self.confirm_set_on_board()
            #if there wasn't a set, shuffle board
            if not set_on_board:
                # print("DEBUG: no set found during reset.")
                self.shuffle_board()
            #if no set, the loop will repeat until it has a set.
        
        # self.current_obs = self.board
        # print("DEBUG: board after reset", self.board)
        return self.board, {}

    def step(self, action):
        """
        Returns: next observation, reward, done, and optional info
        -------
        Given current observation and action, performs the action
        and generates the proper consequences and reward for it.
        """
        # print("Cards in deck:", len(self.deck))
        #convert the action to the indices chosen
        # print("DEBUG: (action in step)", action)
        card_indices = self.action_options[action] #will get 3 numbers, the positions where the cards are
        # print("DEBUG: (card_indices from action)", card_indices)
        # find result of action
        good_set = self.check_set(self.board, card_indices)
        
        if good_set:
            self.board = np.delete(self.board, card_indices) #get rid of cards used
            self.add_cards(3) #replace the three cards removed
            #make sure deck has a set if getting low.
            if len(self.deck)<9:
                #With few cards left in deck, check to see if there is a set left
                if self.confirm_set_on_board(board_only=False):
                    #if no set is left, end the game
                    self.done=True
            self.reward=(69-len(self.deck))/3 #This gives better rewards the further into the deck you get
        else:
            self.reward=-.1
            #There is guaranteed a set on board, so don't change anything.
        
        #If there aren't any cards left in deck, the game is over
        if len(self.deck)==0:
            self.done=True #says the game is done or not.
        #       observation,  reward,     done,   truncated, info
        return self.board, self.reward, self.done, False, {} 

    def gen_card_vals(self):
        cards = [0]*81
        for i in range(4):
            temp = [1*(10**i)]*(3**i)+[2*(10**i)]*(3**i)+[3*(10**i)]*(3**i)
            temp = temp*(3**(3-i))
            cards = [sum(x) for x in zip(cards, temp)]
        return cards
    
    def add_cards(self, num):
        #take three cards from the deck
        cards_to_add, self.deck = self.deck[-num:], self.deck[:-num]
        #add the cards to the board
        self.board = np.append(self.board, cards_to_add).astype(np.uint8)
        # print(self.board)
        #sorting the cards, because it should make it easier to learn.
        self.board = np.sort(self.board)
        # make sure the board has a set on it.
        set_confirmed = False
        while not set_confirmed and not self.done: #The done is in here because if the game is done, you don't need to check
            #check board for set
            set_confirmed = self.confirm_set_on_board()
            #if there wasn't a set, shuffle board
            if not set_confirmed:
                self.shuffle_board()
            #if no set, the loop will repeat until it has a set.
        
    def confirm_set_on_board(self, board_only=True):
        # print("DEBUG: CONFIRMING SET ON BOARD")
        if board_only: #only do board
            # temp_deck = np.arange(len(self.board))
            temp_deck = self.board[:]#make a copy of the board
            
        else: #do board and deck
            # temp_deck = np.arange(len(self.board)+len(self.deck))
            temp_deck = np.append(self.board, self.deck) #add the deck and board together
            
        set_found = False #defaults to no set
        all_card_combos = [list(tup) for tup in itertools.combinations(np.arange(len(temp_deck)), 3)] #finds all possible 3 card combos
        # print(all_card_combos)
        for three_card_set in all_card_combos:
            # print(type(three_card_set))
            # print(three_card_set)
            if self.check_set(temp_deck, three_card_set, action=False):
                set_found = True #Found a set, set this to true
                break #Only need to find one, exit loop
        return set_found

    def shuffle_board(self):
        self.deck = np.append(self.deck, self.board)
        self.board = np.array([])
        # print("Debug: board after setting to empy array", self.board)
        np.random.shuffle(self.deck)
        self.add_cards(12)
        
    def check_set(self, board, tcs, action=True):
        # if action:
            # print("DEBUG (TCS, action, type):", tcs, action, type(tcs))  
        card_indices = [board[i] for i in tcs]
        # print("DEBUG: (card_indices in checkset)", card_indices)
        card_vals = [self.cardvalues[i-1] for i in card_indices]
        total_val= sum(card_vals)
        att1 = int(total_val%10) #ones place
        att2 = int((total_val//10)%10) #tens place
        att3 = int((total_val//100)%10) #hundreds place
        att4 = int((total_val//1000)%10) #thousands place
        if((att1%3!=0) or (att2%3!=0) or (att3%3!=0) or (att4%3!=0)):
            #SET theory (about the game SET we are playing, not actual set theory)
            # says that this is a surefire way of checking if it is a set.
            # can explain in posts, not in code comments. check website if interested.
            return False
        else:
            return True
    
    def render(self, mode='human'):
        """
        Shows the current environment state. 
        Needs implementation, but a  pass can be done if not needed.
        """
        #skipping this step for now.
        pass
    
    def close(self):
        """
        Cleans up resources. 
        """
        #skipping this step for now.
        pass
    
    def seed(self, seed=None):
        """
        makes rng seeds. 
        """
        #skipping this step for now.
        pass


models_dir = "models/PPO"
logdir = "logs"

if not os.path.exists(models_dir):
    os.makedirs(models_dir)
if not os.path.exists(logdir):
    os.makedirs(logdir)
    
env = SetGameEnv()
check_env(env)


env.reset()
# print("sample action:", env.action_space.sample())
# print("observation space shape", env.observation_space.shape)
# print("sample observation", env.observation_space.sample())
# model = A2C("MlpPolicy", env, verbose=1)
# model.learn(total_timesteps=100)

model = PPO("MlpPolicy", env, verbose=1, tensorboard_log=logdir)
timesteps = 10000
for i in range(1,30):
    model.learn(total_timesteps=timesteps, reset_num_timesteps=False, tb_log_name="PPO")
    model.save(f"{models_dir}/{timesteps*i}")
# model.learn(total_timesteps=100000)


vec_env = model.get_env()
episodes = 1
for ep in range(episodes):
    obs= vec_env.reset()
    done = False
    while not done:
        # action, _= model.predict(obs)
        obs, reward, done, truncated, info = env.step(env.action_space.sample())
        
        
episodes = 10
for ep in range(episodes):
    print(ep)
    obs = vec_env.reset()
    done = False
    while not done:
        action, _states = model.predict(obs)
        # print(obs)
        # print(action)
        # print(action)
        # print(action[0][0])
        obs, reward, done, info = vec_env.step(action)

env.close()

















