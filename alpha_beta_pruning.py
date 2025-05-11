from constants import Player


def alpha_beta(game, depth, alpha, beta, maximizing):
    if depth == 0 or game.is_terminal():
        return game.evaluate(), None

    best_move = None

    if maximizing:
        max_eval = float("-inf")

        for move in game.get_possible_moves():
            new_game = game.clone()
            new_game.make_move(move)
            eval, _ = alpha_beta(
                new_game, depth - 1, alpha, beta, new_game.current_player == Player.AI
            )

            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)

            if beta <= alpha:
                break

        return max_eval, best_move

    else:
        min_eval = float("inf")

        for move in game.get_possible_moves():
            new_game = game.clone()
            new_game.make_move(move)
            eval, _ = alpha_beta(
                new_game, depth - 1, alpha, beta, new_game.current_player == Player.AI
            )

            if eval < min_eval:
                min_eval = eval
                best_move = move

            beta = min(beta, eval)

            if beta <= alpha:
                break

        return min_eval, best_move
