# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 19:09:43 2023

@author: gameb
"""

import numpy as np
import itertools

a = np.arange(1,13)
# b = [a.copy(),a.copy(),a.copy()]
c = np.array(list(itertools.combinations(a,3)))

class SetGame():
    
    def __init__(self):
        #Make deck of 81 cards
        self.deck = np.arange(1,82)
        #shuffle it 
        np.random.shuffle(self.deck)
        #Add 12 of the cards to the board
        self.board = self.add_cards(12)
        self.score = 0 #initialize score at 0
        #this is for checking sets
        self.cardvalues = self.gen_card_vals()
        #Make a list of all possible combinations of 3 cards of 12
        choices = np.array(list(itertools.combinations(np.arange(12),3)))
        self.actions = [0]+choices #add option for saying no set on board
        #Made to check the game history #SKIPPED FOR NOW
        # init_state = self.board.copy()
        # self.history = [init_state]
        
    def step(self, action):
        # self.history.append(action)
        if action == [0]:
            #If the ai said there wasn't a set
            if self.confirm_set_on_board():
                self.score -= 1 #punishes for not seeing a set.
            else:
                self.score += 1 #rewards for seeing there isn't a set
                #If there isn't a set on board
                if self.check_deck_for_set():
                    self.shuffleboard()
                else:
                    self.board = [0] #if there isn't a set in deck, end the game.
        else:
            if self.check_set(action):
                self.score += 1
                self.board = np.delete(self.board, action) #get rid of cards used
                self.add_cards(3) #add three cards to the board
            else:
                self.score -= 0.1 #punish for incorrect guess
        
        
        
    def check_set(self, tcs):
        card_vals = [self.cardvalues[tcs[i]] for i in tcs]
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
        
    def gen_card_vals(self):
        cards = [0]*81
        for i in range(4):
            temp = [1*(10**i)]*(3**i)+[2*(10**i)]*(3**i)+[3*(10**i)]*(3**i)
            temp = temp*(3**(3-i))
            cards = [sum(x) for x in zip(cards, temp)]
        return cards
    
    def add_cards(self, num):
        for i in range(num):
            self.board.append(self.deck.pop())
        #sorting the cards, because it will make it easier to learn.
        self.board = np.sort(self.board)
        
    def confirm_set_on_board(self, board_only=True):
        if board_only: #only do board
            temp_deck = self.board.copy()#make a copy of the board
        else: #do board and deck
            temp_deck = self.board.copy() + self.deck.copy() #add the deck and board together
        set_found = False #defaults to no set
        all_card_combos = itertools.combinations(temp_deck, 3) #finds all possible 3 card combos
        for three_card_set in all_card_combos:
            if self.check_set(three_card_set):
                set_found = True #Found a set, set this to true
                break #Only need to find one, exit loop
        return set_found

    def shuffle_board(self):
        self.deck += self.board
        np.random.shuffle(self.deck)
        self.add_cards(12)
        
        
        
        
        ############
                
    
    

        
                    
















dealer_scores = np.arange(1, 11)
player_scores = np.arange(1, 22)
states = [(dealer_score, player_score) for player_score in player_scores for dealer_score in dealer_scores] 
















