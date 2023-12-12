# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 12:31:31 2023

@author: gameb
"""

from gymnasium import Env, spaces
import numpy as np
import itertools
# from stable_baselines3 import PPO, A2C
# from stable_baselines3.common.env_checker import check_env
# import os

class SetGameEnvEasy(Env):
    def __init__(self):
        """
        Creates the space needed, and some others for testing
        Needs the observation_space and action_space
        """
        super(SetGameEnvEasy, self).__init__()
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
        temp_deck = np.arange(6)
        self.action_options = [list(tup) for tup in itertools.combinations(temp_deck, 3)]
        self.action_space = spaces.Discrete(20)
        
        
        self.observation_space = spaces.Box(
            low=1,
            high=27,
            shape=(6,), 
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
        self.deck = np.arange(1,28).astype(np.uint8)
        self.board = np.array([])
        #shuffle it 
        np.random.shuffle(self.deck)
        #Add 12 of the cards to the board
        # print("DEBUG: no cards should be here:", self.board)
        self.add_cards(6)
        # print("board:",self.board)
        set_on_board = False
        # stop_loop = 0
        while not set_on_board:
            # stop_loop += 1
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
            
            #make sure deck has a set if getting low.
            if len(self.deck)<10:
                #With few cards left in deck, check to see if there is a set left
                if self.confirm_set_on_board(board_only=False):
                    #if no set is left, end the game
                    self.done=True
            # self.reward=(21-len(self.deck))/3 #This gives better rewards the further into the deck you get
            self.reward=1 #This gives a consistent reward
            if not self.done:
                self.add_cards(3) #replace the three cards removed
        else:
            self.reward=-.2 #small negative reward as punishment
            #There is guaranteed a set on board, so don't change anything.
            
        
        #If there aren't any cards left in deck, the game is over
        if len(self.deck)==0:
            self.done=True #says the game is done or not.
        #       observation,  reward,     done,   truncated, info
        return self.board, self.reward, self.done, False, {} 
    
    # For the travel(easy) version, only three attributes are generated.
    def gen_card_vals(self):
        cards = [0]*27
        for i in range(3):
            temp = [1*(10**i)]*(3**i)+[2*(10**i)]*(3**i)+[3*(10**i)]*(3**i)
            temp = temp*(3**(3-i))
            cards = [sum(x) for x in zip(cards, temp)]
        return cards
    # #Regular version has 4 attributes
    # def gen_card_vals(self):
    #     cards = [0]*81
    #     for i in range(4):
    #         temp = [1*(10**i)]*(3**i)+[2*(10**i)]*(3**i)+[3*(10**i)]*(3**i)
    #         temp = temp*(3**(3-i))
    #         cards = [sum(x) for x in zip(cards, temp)]
    #     return cards
    
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
        self.add_cards(6)
        
    def check_set(self, board, tcs, action=True):
        # Because 0+0+0%3==0, this doesn't need to change between easy and normal version of set
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


# test = spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32)
# test.sample()
# test = spaces.Box(low=0, high=1, dtype=np.float32)
# test.sample()

# test = spaces.Box(
#     low=0,
#     high=1,
#     shape=(27,),
#     dtype=np.bool_)
# test.sample()

class SetGameEnvEasyBox(Env):
    def __init__(self):
        """
        Creates the space needed, and some others for testing
        Needs the observation_space and action_space
        """
        super(SetGameEnvEasyBox, self).__init__()
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
        temp_deck = np.arange(27)
        self.board_options = [list(tup) for tup in itertools.combinations(temp_deck, 3)]
        temp_deck = np.arange(6)
        self.action_options = [list(tup) for tup in itertools.combinations(temp_deck, 3)]
        self.action_choice = []
        self.board_indices=[0]*3
        # self.action_space = spaces.Discrete(20)
        self.action_space = spaces.Box(low=-1, high=1)
        
        # self.observation_space = spaces.Box(
        #     low=1,
        #     high=27,
        #     shape=(6,), 
        #     dtype=np.uint8)
        self.observation_space = spaces.Box(
            low=0,
            high=1,
            shape=(27,),
            dtype=np.bool_)
        self.cards_on_board = np.array([False]*27)

    def reset(self, seed=0):
    # def reset(self):
        """
        Returns: the observation of the initial state
        -------
        Resets the environment to initial state so a new episode can start
        The new episodes should be independent from previous ones
        """
        self.done = False
        self.deck = np.arange(1,28).astype(np.uint8)
        self.board = np.array([])
        #shuffle it 
        np.random.shuffle(self.deck)
        #Add 12 of the cards to the board
        # print("DEBUG: no cards should be here:", self.board)
        self.add_cards(6)
        # print("board:",self.board)
        set_on_board = False
        # stop_loop = 0
        while not set_on_board:
            # stop_loop += 1
            #check board for set
            set_on_board = self.confirm_set_on_board()
            #if there wasn't a set, shuffle board
            if not set_on_board:
                # print("DEBUG: no set found during reset.")
                self.shuffle_board()
            #if no set, the loop will repeat until it has a set.

        # print("DEBUG: board after reset", self.board)
        
        #cards_on_board is changed in the add_cards() function
        return self.cards_on_board, {}

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
        # card_indices = self.action_options[action] #will get 3 numbers, the positions where the cards are
        # print("DEBUG: (card_indices from action)", card_indices)
        card_choice = int((action+1)*2924/2)#multiply the action by length of board_options-1. Because range of box is -1 to 1, ajust that too.
        card_indices= np.array(self.board_options[card_choice])
        #check to see if the cards chosen are actually on the board.
        #       each of the cards_on_board should be true foreach index chosen, aka all cards chosen are actually on the board.
        valid_choice = (self.cards_on_board[card_indices[0]] and self.cards_on_board[card_indices[1]] and self.cards_on_board[card_indices[2]])
        # find result of action
        if not valid_choice:
            self.reward = -.01 #very small punishment for choosing cards that aren't on board
            
        #If it is a valid choice, check if the set is a good set or not, and adjust things accordingly
        else:
            #find where on board those cards are
            # debugging = self.board[:]
            # print("DEBUG: card_indices", card_indices)
            # print("DEBUG: board:", debugging)
            
            for i in range(len(card_indices)):
                #   add 1 do values because the board is values from 1-27, not 0-26
                self.board_indices[i] = np.where(self.board==card_indices[i]+1)[0][0]
            good_set = self.check_set(self.board, self.board_indices)
            
            if good_set:
                #get rid of cards used
                self.board = np.delete(self.board, self.board_indices) 
                # for index in board_indices:
                #     self.cards_on_board[index] = False
                
                #make sure deck has a set if getting low.
                if len(self.deck)<50:
                    #With few cards left in deck, check to see if there is a set left
                    if self.confirm_set_on_board(board_only=False):
                        #if no set is left, end the game
                        self.done=True
                # self.reward=(21-len(self.deck))/3 #This gives better rewards the further into the deck you get
                self.reward=10 #This gives a consistent reward
                if not self.done:
                    self.add_cards(3) #replace the three cards removed
            else:
                self.reward=-.1 #small negative reward as punishment
                #There is guaranteed a set on board, so don't change anything.
                
            
            #If there aren't any cards left in deck, the game is over
            if len(self.deck)==0:
                self.done=True #says the game is done or not.
            #       observation,        reward,     done,     truncated, info
        return self.cards_on_board, self.reward, self.done, False, {} 
    
    # For the travel(easy) version, only three attributes are generated.
    def gen_card_vals(self):
        cards = [0]*27
        for i in range(3):
            temp = [1*(10**i)]*(3**i)+[2*(10**i)]*(3**i)+[3*(10**i)]*(3**i)
            temp = temp*(3**(3-i))
            cards = [sum(x) for x in zip(cards, temp)]
        return cards
    # #Regular version has 4 attributes
    # def gen_card_vals(self):
    #     cards = [0]*81
    #     for i in range(4):
    #         temp = [1*(10**i)]*(3**i)+[2*(10**i)]*(3**i)+[3*(10**i)]*(3**i)
    #         temp = temp*(3**(3-i))
    #         cards = [sum(x) for x in zip(cards, temp)]
    #     return cards
    
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
        #once the board is finalized, change the cards_on_board for the observation space
        self.cards_on_board = np.array([False]*27)
        for index in self.board:
            self.cards_on_board[index-1] = True
        
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
        self.add_cards(6)
        
    def check_set(self, board, tcs, action=True):
        # Because 0+0+0%3==0, this doesn't need to change between easy and normal version of set
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
