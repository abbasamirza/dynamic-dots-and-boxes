from constants import Player


class DotsAndBoxesGame:
    def __init__(self, size):
        self.size = size  # This is the size of the grid
        self.lines = {}  # This stores the lines drawn
        self.boxes = {}  # This stores the boxes that are captured
        self.current_player = (
            Player.PLAYER
        )  # This stores the current player (defaults to Player, but first move is random)
        self.power_tokens = {
            Player.PLAYER: 0,
            Player.AI: 0,
        }  # This stores the number of power tokens each player has
        self.turn_count = 0  # This stores the number of turns taken
        self.last_move = None  # This stores the last move made
        self.last_move_done_by = None  # This stores the last move done by which player
        self.power_used_this_turn = (
            False  # This stores whether a power token was used this turn
        )

    def clone(self):
        new_game = DotsAndBoxesGame(self.size)
        new_game.lines = self.lines.copy()
        new_game.boxes = self.boxes.copy()
        new_game.current_player = self.current_player
        new_game.power_tokens = self.power_tokens.copy()
        new_game.turn_count = self.turn_count
        new_game.last_move = self.last_move
        new_game.last_move_done_by = self.last_move_done_by
        new_game.power_used_this_turn = self.power_used_this_turn

        return new_game

    def make_move(self, move):
        self.lines[move] = self.current_player
        self.turn_count += 1
        claimed = False

        for box in self.get_adjacent_boxes(move):
            if self.is_box_completed(box) and box not in self.boxes:
                self.boxes[box] = self.current_player
                if self.power_tokens[self.current_player] == 0:
                    self.power_tokens[self.current_player] = 1
                claimed = True

        if self.last_move_done_by != self.current_player:
            self.power_used_this_turn = False

        self.last_move = move
        self.last_move_done_by = self.current_player

        if not claimed:
            self.current_player = (
                Player.AI if self.current_player == Player.PLAYER else Player.PLAYER
            )

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
        x1, y1, x2, _ = line
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
