from constants import Player


class DotsAndBoxesGame:
    def __init__(self, size):
        self.size = size
        self.lines = set()
        self.boxes = {}
        self.current_player = Player.PLAYER

    def clone(self):
        new_game = DotsAndBoxesGame(self.size)
        new_game.lines = self.lines.copy()
        new_game.boxes = self.boxes.copy()
        new_game.current_player = self.current_player
        return new_game

    def make_move(self, move):
        self.lines.add(move)
        claimed_box = False

        for box in self.get_adjacent_boxes(move):
            if self.is_box_completed(box) and box not in self.boxes:
                self.boxes[box] = self.current_player
                claimed_box = True

        if not claimed_box:
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
                v = (y, x, y, x + 1)
                if h not in self.lines:
                    moves.append(h)
                if v not in self.lines:
                    moves.append(v)
        return moves

    def get_adjacent_boxes(self, line):
        x1, y1, x2, y2 = line
        boxes = []
        if x1 == x2:  # vertical
            top_box = (x1 - 1, y1) if x1 > 0 else None
            bottom_box = (x1, y1) if x1 < self.size - 1 else None
        else:  # horizontal
            top_box = (x1, y1 - 1) if y1 > 0 else None
            bottom_box = (x1, y1) if y1 < self.size - 1 else None
        if top_box:
            boxes.append(top_box)
        if bottom_box:
            boxes.append(bottom_box)
        return boxes

    def is_terminal(self):
        return len(self.lines) >= (self.size - 1) * self.size * 2

    def evaluate(self):
        player_score = sum(1 for v in self.boxes.values() if v == Player.PLAYER)
        ai_score = sum(1 for v in self.boxes.values() if v == Player.AI)
        return ai_score - player_score
