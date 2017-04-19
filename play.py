# -*- coding: utf-8 -*-
"""Simple, face up console version of game"""

import argparse

import numpy as np

from loveletter import game
from loveletter.game import Game
from loveletter.player import PlayerAction, PlayerActionTools, PlayerTools
from loveletter.card import Card


PARSER = argparse.ArgumentParser(
    description='Play a console Love Letter game')

PARSER.add_argument('--seed', type=int, default=451,
                    help='Seed to populate game')
PARSER.add_argument('--replay', type=str, default="",
                    help='Actions to replay (copied from previous output)')

ARGS = PARSER.parse_args()

# def actions_to_str(actions):
#     np_arr = [PlayerActionTools.to_np_many]


def display(game, actions):
    """Print a game to the console"""
    lst = [str(i) for i in PlayerActionTools.to_np_many(actions)]
    print(",".join(lst))
    for line in game.to_str():
        print(line)


def get_int(prompt):
    """Prompt until proper value given"""
    print(prompt)
    while True:
        try:
            return int(input(" > "))
        except ValueError:
            print("Invalid Entry - Exit with Ctrl-C")


def get_action():
    """Get a player action from the console"""
    discard = get_int("Discard Card")
    player_target = get_int("Player Target")
    guess = get_int("Guessed Card") if discard == Card.guard else 0
    return PlayerAction(discard, player_target, guess, 0)


player_index = 1
# def grab_reward():
#     """
#     Record current reward.
#     """
#     while Game.active() == True:
#         # if Game.action() == _invalid_input(throw):
#         #     return -1
#         # else:
#         return 0
#     if Game.winner() == player_index:
#         return 30
#     else:
#         return -10


def play(seed, previous_actions):
    """Play a game"""
    game = Game.new(4, seed)
    previous_actions = np.array([], dtype=np.uint8) if len(previous_actions) < 1 else \
        np.array([int(i) for i in previous_actions.split(",")], dtype=np.uint8)
    previous_actions = PlayerActionTools.from_np_many(previous_actions)[::-1]
    actions = []
    rewards = []
    while game.active():
        if not game.is_current_player_playing():
            game = game.skip_eliminated_player()
            continue

        display(game, actions)

        try:
            if len(previous_actions) > 0:
                action = previous_actions.pop()
            else:
                print("  What card to play?")
                action = get_action()
                reward = 0
            actions.append(action)
            rewards.append(reward)
            game = game.move(action)
        except ValueError:
            reward = -1
            print("Invalid move - Exit with Ctrl-C")

    display(game, actions)
    if game.winner() == player_index:
        reward = 30
    else:
        reward = -10
    rewards.append(reward)
    print(rewards)
    print("Game Over : Player {} Wins!".format(game.winner()))

if __name__ == "__main__":
    play(ARGS.seed, ARGS.replay)
