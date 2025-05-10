from logic import DotsAndBoxesGame

def minimax(game, depth, maximizing):
    if depth == 0 or game.is_terminal():
        return game.evaluate(), None

    best_move = None
    if maximizing:
        max_eval = float('-inf')
        for move in game.get_possible_moves():
            new_game = game.clone()
            new_game.make_move(move)
            eval = minimax(new_game, depth - 1, new_game.current_player == "ai")[0]
            if eval > max_eval:
                max_eval = eval
                best_move = move
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in game.get_possible_moves():
            new_game = game.clone()
            new_game.make_move(move)
            eval = minimax(new_game, depth - 1, new_game.current_player == "ai")[0]
            if eval < min_eval:
                min_eval = eval
                best_move = move
        return min_eval, best_move
