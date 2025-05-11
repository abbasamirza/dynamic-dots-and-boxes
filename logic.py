from constants import Player
import random


class DotsAndBoxesGame:
    def __init__(self, size):
        self.size = size
        self.lines = {}
        self.boxes = {}
        self.current_player = Player.PLAYER
        self.power_tokens = {Player.PLAYER: 0, Player.AI: 0}
        self.turn_count = 0
        self.last_move = None
        self.bonus_boxes = set()
        self.initialize_bonus_boxes()
        self.used_token_this_turn = False

    def initialize_bonus_boxes(self):
        total_boxes = (self.size - 1) * (self.size - 1)
        num_bonus = max(1, total_boxes // 10)
        all_boxes = [(x, y) for x in range(self.size - 1) for y in range(self.size - 1)]
        self.bonus_boxes = set(random.sample(all_boxes, num_bonus))

    def clone(self):
        new_game = DotsAndBoxesGame(self.size)
        new_game.lines = self.lines.copy()
        new_game.boxes = self.boxes.copy()
        new_game.current_player = self.current_player
        new_game.power_tokens = self.power_tokens.copy()
        new_game.turn_count = self.turn_count
        new_game.bonus_boxes = self.bonus_boxes.copy()
        new_game.last_move = self.last_move
        return new_game

    def make_move(self, move):
        self.lines[move] = self.current_player
        self.turn_count += 1
        claimed = False

        for box in self.get_adjacent_boxes(move):
            if self.is_box_completed(box) and box not in self.boxes:
                self.boxes[box] = self.current_player
                # only award if they have 0 tokens
                if self.power_tokens[self.current_player] == 0:
                    self.power_tokens[self.current_player] = 1
                claimed = True

        # record last move for “reversal”
        self.last_move = move

        # switch sides only if they didn’t just claim a box
        if not claimed:
            self.current_player = (
                Player.AI if self.current_player == Player.PLAYER else Player.PLAYER
            )
        # reset the “used token” flag if it’s AI’s turn now
        if self.current_player == Player.AI:
            self.used_token_this_turn = False

    def is_box_completed(self, box):
        x, y = box
        return all(
            [
                ((x, y, x + 1, y)) in self.lines,
                ((x, y, x, y + 1)) in self.lines,
                ((x + 1, y, x + 1, y + 1)) in self.lines,
                ((x, y + 1, x + 1, y + 1)) in self.lines,
            ]
        )

    def get_possible_moves(self):
        moves = []
        for y in range(self.size):
            for x in range(self.size - 1):
                h = (x, y, x + 1, y)
                if h not in self.lines:
                    moves.append(h)
        for y in range(self.size - 1):
            for x in range(self.size):
                v = (x, y, x, y + 1)
                if v not in self.lines:
                    moves.append(v)
        return moves

    def get_adjacent_boxes(self, line):
        x1, y1, x2, y2 = line
        boxes = []
        if x1 == x2:
            top_box = (x1 - 1, y1) if x1 > 0 else None
            bottom_box = (x1, y1) if x1 < self.size - 1 else None
        else:
            top_box = (x1, y1 - 1) if y1 > 0 else None
            bottom_box = (x1, y1) if y1 < self.size - 1 else None
        if top_box:
            boxes.append(top_box)
        if bottom_box:
            boxes.append(bottom_box)
        return boxes

    def is_terminal(self):
        return len(self.lines) >= 2 * self.size * (self.size - 1)

    def evaluate(self):
        player_score = sum(1 for v in self.boxes.values() if v == Player.PLAYER)
        ai_score = sum(1 for v in self.boxes.values() if v == Player.AI)
        return ai_score - player_score
