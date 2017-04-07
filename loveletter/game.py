# -*- coding: utf-8 -*-
"""
Love Letter Game object
"""

from loveletter.card import Card
from loveletter.player import Player, PlayerTools, PlayerAction, PlayerActionTools


class Game():
    """A Love Letter Game"""

    def __init__(self, deck, players, turn_index):
        self._deck = deck
        self._players = players
        self._turn_index = turn_index

        # TODO: check if game is over

    def players(self):
        """List of current players."""
        return self._players[:]

    def deck(self):
        """
        List of current cards.

        NOTE: The LAST card [-1] is always held out
        """
        return self._deck

    def turn_index(self):
        """
        Overall turn index of the game.

        This points to the actual action number
        """
        return self._turn_index

    def round(self):
        """Current round number."""
        return self._turn_index // len(self._players)

    def player_turn(self):
        """Player number of current player."""
        return self._turn_index % len(self._players)

    def _player(self):
        """Returns the current player"""
        return self._players[self.player_turn()]

    def move(self, action, throw=False):
        """Current player makes an action."""
        if not self.is_action_valid(action):
            return self._invalid_input(throw)

        # player is out, increment turn index
        if action.discard == Card.noCard:
            return Game(self.deck(), self.players(), self.turn_index() + 1)

        player = self._players[self.player_turn()]
        player_hand = [player.hand_card, self._deck[0]]

        player_hand_new = Game.new_hand_card(action.card_discard, player_hand)
        deck_new = self._deck[1:]

        # priest requires modification of action (knowledge)
        if action.discard == Card.priest:
            return self._move_priest(action, player_hand_new, deck_new)

        # updated players for the next turn
        player_moved = PlayerTools.move(
            self._player(), player_hand_new, action)
        current_players = Game._set_player(
            self._players, player_moved, self.player_turn())

        if action.discard == Card.guard:
            return self._move_guard(current_players, action, deck_new)

        raise NotImplementedError("Missing game logic")

    def _move_guard(self, current_players, action, deck_new):
        """Handle a guard action into a new game state"""

        if self._players[action.player_target].hand_card == action.guess:
            # then target player is out
            player_target = PlayerTools.force_discard(
                self._players[action.player_target])
            current_players = Game._set_player(
                current_players, player_target, action.player_target)

        return Game(deck_new, current_players, self._turn_index + 1)

    def _move_priest(self, action, player_hand_new, deck_new):
        """Handle a priest action into a new game state"""
        player_targets_card = self._players[action.player_target].hand_card
        action_updated = PlayerAction(
            action.discard, action.player_target, action.guess, player_targets_card)

        player = PlayerTools.move(
            self._player(), player_hand_new, action_updated)
        current_players = Game._set_player(
            self._players, player, self.player_turn())

        return Game(deck_new, current_players, self._turn_index + 1)

    def _move_baron(self, action, player_hand_new, deck_new):
        """Handle a baron action into a new game state"""
        raise NotImplementedError("Missing game logic")

    def _move_handmaid(self, action, player_hand_new, deck_new):
        """Handle a handmaid action into a new game state"""
        raise NotImplementedError("Missing game logic")

    def _move_prince(self, action, player_hand_new, deck_new):
        """Handle a prince action into a new game state"""
        raise NotImplementedError("Missing game logic")

    def _move_king(self, action, player_hand_new, deck_new):
        """Handle a king action into a new game state"""
        raise NotImplementedError("Missing game logic")

    def _move_countess(self, action, player_hand_new, deck_new):
        """Handle a countess action into a new game state"""
        raise NotImplementedError("Missing game logic")

    def _move_princess(self, action, player_hand_new, deck_new):
        """Handle a princess action into a new game state"""
        raise NotImplementedError("Missing game logic")

    def is_action_valid(self, action):
        """Tests if an action is valid given the current game state"""
        player = self._players[self.player_turn()]

        # if player is out, only valid action is no action
        if player.hand_card == Card.noCard:
            return PlayerActionTools.is_blank(action)

        target_player = self._players[action.player_target]
        player_hand = [player.hand_card, self._deck[0]]

        # cannot discard a card not in the hand
        if action.discard not in player_hand:
            return False

        # cannot target an invalid player
        if not self._is_valid_player_target(action.player_target):
            return False

        # cannot mis-target a card
        if self.player_turn() == action.player_target and action.discard in Card.only_other:
            return False
        if self.player_turn() != action.player_target and action.discard in Card.only_self:
            return False

        if not PlayerTools.is_playing(target_player):
            return False

        # Cannot guess guard or no card
        if action.discard == Card.guard and (
                action.guess == Card.guard or action.guess == Card.noCard):
            return False

        return True

    def _is_valid_player_target(self, player_target):
        """True iff the player can be targeted by an action"""
        return PlayerTools.is_playing(self._players[player_target])

    def _invalid_input(self, throw):
        """Throw if true, otherwise return current game"""
        if throw:
            raise Exception("Invalid Move")
        return self

    @staticmethod
    def _set_player(players, player_new, player_new_index):
        """Return a fresh copy of players with the new player in the index"""
        players_new = players[:]
        players_new[player_new_index] = player_new
        return players

    @staticmethod
    def new_hand_card(card_discard, hand):
        """New hand card based on current cards in hand"""
        new_hand = list(filter(lambda card: card != card_discard, hand))
        if len(new_hand) < 1:
            # this means the hand contained only one card. so one still remains
            return card_discard
        return new_hand[0]

    @staticmethod
    def new(player_count=4, seed=451):
        """Create a brand new game"""
        deck = Card.shuffle_deck(seed)

        dealt_cards = deck[:player_count]
        undealt_cards = deck[player_count:]

        players = list(map(PlayerTools.blank, dealt_cards))
        return Game(undealt_cards, players, 0)
