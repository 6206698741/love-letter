# -*- coding: utf-8 -*-
"""
Love Letter Game object
"""

from loveletter.card import Card
from loveletter.player import PlayerTools, PlayerAction, PlayerActionTools


class Game():
    """A Love Letter Game"""

    def __init__(self, deck, players, turn_index):
        self._deck = deck
        self._players = players
        self._turn_index = turn_index

        total_playing = sum([1 for player in players if PlayerTools.is_playing(player)])
        self._game_active = total_playing > 1

    def players(self):
        """List of current players."""
        return self._players[:]

    def deck(self):
        """
        List of current cards.

        NOTE: The LAST card [-1] is always held out
        """
        return self._deck

    def draw_card(self):
        """
        Card currently available to the next player.

        Only valid if the game is not over.
        """
        return self._deck[0]

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

    def cards_left(self):
        """
        Number of cards left in deck to distribute

        Does not include the held back card
        """
        return len(self._deck) - 1

    def active(self):
        """Return True if the game is still playing"""
        return self._game_active

    def over(self):
        """Return True if the game is over"""
        return not self.active()

    def move(self, action, throw=False):
        """Current player makes an action."""
        if self.over() or not self.is_action_valid(action):
            return self._invalid_input(throw)

        # player is out, increment turn index
        if action.discard == Card.noCard:
            return Game(self.deck(), self.players(), self.turn_index() + 1)

        player = self._player()
        player_hand = [player.hand_card, self._deck[0]]
        player_hand_new = Game.new_hand_card(action.card_discard, player_hand)
        deck_new = self._deck[1:]

        # choosing to discard the princess ... is valid
        if action.discard == Card.princess:
            return self._move_princess(player_hand_new, deck_new)

        # priest requires modification of action (knowledge)
        if action.discard == Card.priest:
            return self._move_priest(action, player_hand_new, deck_new)
        if action.discard == Card.baron:
            return self._move_baron(action, player_hand_new, deck_new)

        # updated players for the next turn
        player = PlayerTools.move(self._player(), player_hand_new, action)
        current_players = Game._set_player(
            self._players, player, self.player_turn())

        # No other logic for handmaids or countess
        if action.discard == Card.handmaid or \
                action.discard == Card.countess:
            return Game(deck_new, current_players, self._turn_index + 1)

        if action.discard == Card.guard:
            return self._move_guard(current_players, action, deck_new)

        if action.discard == Card.prince:
            return self._move_prince(current_players, action, deck_new)

        if action.discard == Card.king:
            return self._move_king(current_players, action, deck_new)

        raise NotImplementedError("Missing game logic")

    def _move_guard(self, current_players, action, deck_new):
        """
        Handle a guard action into a new game state

        Player makes a guess to try and eliminate the opponent
        """
        if self._players[action.player_target].hand_card == action.guess and \
                not PlayerTools.is_defended(self._players[action.player_target]):
            # then target player is out
            player_target = PlayerTools.force_discard(
                self._players[action.player_target])
            current_players = Game._set_player(
                current_players, player_target, action.player_target)

        return Game(deck_new, current_players, self._turn_index + 1)

    def _move_priest(self, action, player_hand_new, deck_new):
        """
        Handle a priest action into a new game state

        Action gains knowledge of other player's card
        """
        player_targets_card = Card.noCard if \
            PlayerTools.is_defended(self._players[action.player_target]) \
            else self._players[action.player_target].hand_card
        action_updated = PlayerAction(
            action.discard, action.player_target, action.guess, player_targets_card)

        player = PlayerTools.move(
            self._player(), player_hand_new, action_updated)
        current_players = Game._set_player(
            self._players, player, self.player_turn())

        return Game(deck_new, current_players, self._turn_index + 1)

    def _move_baron(self, action, player_hand_new, deck_new):
        """
        Handle a baron action into a new game state

        Player and target compare hand cards. Player with lower hand
        card is eliminated
        """
        card_target = self._players[action.player_target].hand_card
        if player_hand_new > card_target:
            if not PlayerTools.is_defended(self._players[action.player_target]):
                # target is eliminated
                player_target = PlayerTools.force_discard(
                    self._players[action.player_target])
                current_players = Game._set_player(
                    self._players, player_target, action.player_target)
        else:
            # player is eliminated
            player = PlayerTools.force_discard(self._player())
            current_players = Game._set_player(
                self._players, player, self.player_turn())

        return Game(deck_new, current_players, self._turn_index + 1)

    def _move_prince(self, current_players, action, deck_new):
        """Handle a prince action into a new game state"""

        player_before_discard = self._players[action.player_target]

        # if there are no more cards, this has no effect
        if len(deck_new) - 1 < 1:
            return Game(deck_new, current_players, self._turn_index + 1)

        if player_before_discard.hand_card == Card.princess:
            player_post_discard = PlayerTools.force_discard(
                player_before_discard)
            deck_final = deck_new
        else:
            player_post_discard = PlayerTools.force_discard(
                player_before_discard, deck_new[0])
            deck_final = deck_new[1:]

        current_players = Game._set_player(
            current_players, player_post_discard, action.player_target)

        return Game(deck_final, current_players, self._turn_index + 1)

    def _move_king(self, current_players, action, deck_new):
        """Handle a king action into a new game state"""
        player = self._player()
        target = self._players[action.player_target]

        player_new = PlayerTools.set_hand(player, target.hand_card)
        target_new = PlayerTools.set_hand(target, player.hand_card)

        current_players = Game._set_player(
            current_players, player_new, self.player_turn())
        current_players = Game._set_player(
            current_players, target_new, action.player_target)

        return Game(deck_new, current_players, self._turn_index + 1)

    def _move_princess(self, player_hand, new_deck):
        """Handle a princess action into a new game state"""
        player = PlayerTools.force_discard(self._player(), player_hand)
        player = PlayerTools.force_discard(player)
        current_players = Game._set_player(
            self._players, player, self.player_turn())
        return Game(new_deck, current_players, self._turn_index + 1)

    def is_action_valid(self, action):
        """Tests if an action is valid given the current game state"""
        player = self._player()

        # if player is out, only valid action is no action
        if player.hand_card == Card.noCard:
            return PlayerActionTools.is_blank(action)

        target_player = self._players[action.player_target]
        player_hand = [player.hand_card, self._deck[0]]

        # cannot discard a card not in the hand
        if action.discard not in player_hand:
            return False

        new_hand_card = Game.new_hand_card(action.discard, player_hand)

        # countess must be discarded if the other card is king/prince
        if new_hand_card == Card.countess and \
                (action.discard == Card.prince or action.discard == Card.king):
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
