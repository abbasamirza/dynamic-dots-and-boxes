import pygame, sys, math, random
from logic import DotsAndBoxesGame
from constants import Player, Colors, BUTTON_BACK_SIZE, CONFIRM_DIALOG_SIZE
from minimax import minimax
from alpha_beta_pruning import alpha_beta

pygame.init()

FPS = 60
LINE_WIDTH = 4
DOT_RADIUS = 6
MARGIN = 80

screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
FONT = pygame.font.SysFont("Arial", 28)
BTN_FONT = pygame.font.SysFont("Arial", 24)
SMALL_FONT = pygame.font.SysFont("Arial", 18)
TOKEN_FONT = pygame.font.SysFont("Arial", 14)


def distance_point_to_segment(point, seg_start, seg_end):
    """
    This function calculates the distance from a point to a line
    To allow the drawing of the lines accurately
    """
    (x, y), (x1, y1), (x2, y2) = point, seg_start, seg_end
    dx, dy = x2 - x1, y2 - y1

    if dx == dy == 0:
        return math.hypot(x - x1, y - y1)

    t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    proj = (x1 + t * dx, y1 + t * dy)

    return math.hypot(x - proj[0], y - proj[1])


def draw_text_button(surface, text, rect, hover=False):
    """
    This is a helper function that draws a button with text
    """
    col = Colors.BUTTON_HOVER if hover else Colors.BUTTON_COLOR

    pygame.draw.rect(surface, col, rect, border_radius=10)

    label = BTN_FONT.render(text, True, Colors.WHITE)
    surface.blit(label, label.get_rect(center=rect.center))


def get_line_from_mouse(pos, grid_size, spacing, drawn, offset):
    """
    This function returns the line closest to the mouse position
    """
    ox, oy = offset
    candidates = []

    for r in range(grid_size):
        for c in range(grid_size - 1):
            s = (ox + c * spacing, oy + r * spacing)
            e = (ox + (c + 1) * spacing, oy + r * spacing)
            mv = (c, r, c + 1, r)

            if mv not in drawn:
                candidates.append((distance_point_to_segment(pos, s, e), mv))

    for r in range(grid_size - 1):
        for c in range(grid_size):
            s = (ox + c * spacing, oy + r * spacing)
            e = (ox + c * spacing, oy + (r + 1) * spacing)
            mv = (c, r, c, r + 1)

            if mv not in drawn:
                candidates.append((distance_point_to_segment(pos, s, e), mv))

    if not candidates:
        return None

    best = min(candidates, key=lambda x: x[0])

    return best[1] if best[0] < 20 else None


def draw_power_panel(surface, panel_rect):
    """
    This function draws the power buttons and their info in the left side
    """
    actions = [
        ("Extra Move", "Keep turn without capture"),
        ("Line Reversal", "Undo opponent's last move"),
        ("Swap Token", "Exchange your token", "for a random line"),
    ]
    btn_w, btn_h = panel_rect.width - 40, 50
    gap = 50
    hdr = SMALL_FONT.render("POWER ACTIONS", True, Colors.BLACK)

    surface.blit(hdr, hdr.get_rect(center=(panel_rect.centerx, panel_rect.y + 40)))

    y0 = panel_rect.y + 60
    buttons = {}

    for i, (name, *desc) in enumerate(actions):
        r = pygame.Rect(panel_rect.x + 20, y0 + i * (btn_h + gap), btn_w, btn_h)
        buttons[name] = r

        draw_text_button(surface, name, r, r.collidepoint(pygame.mouse.get_pos()))

        for des in desc:
            d = SMALL_FONT.render(des, True, Colors.BLACK)
            surface.blit(d, (r.x + 10, r.bottom + 10))
            r = pygame.Rect(r.x + 10, r.bottom + 10, btn_w - 20, btn_h)
            r.height = d.get_height() + 5
            y0 += r.height

    return buttons


def draw_score_panel(surface, game, panel_rect):
    """
    This function draws the score panel on the right side
    It shows the number of boxes completed by each player
    And the number of tokens each player has
    """
    hdr = SMALL_FONT.render("SCORE & TOKENS", True, Colors.BLACK)

    surface.blit(hdr, hdr.get_rect(center=(panel_rect.centerx, panel_rect.y + 20)))

    you_boxes = sum(v == Player.PLAYER for v in game.boxes.values())
    ai_boxes = sum(v == Player.AI for v in game.boxes.values())
    lines = [
        f"You: {you_boxes} boxes",
        f"AI:  {ai_boxes} boxes",
        "",
        f"You: {game.power_tokens[Player.PLAYER]} tokens",
        f"AI:  {game.power_tokens[Player.AI]} tokens",
    ]
    y = panel_rect.y + 60

    for txt in lines:
        surf = SMALL_FONT.render(txt, True, Colors.BLACK)
        surface.blit(
            surf, (panel_rect.x + (panel_rect.width - surf.get_width()) // 2, y)
        )
        y += surf.get_height() + 5


def draw_info_panel(surface, panel_rect):
    """
    This function draws the information panel at the bottom
    It shows the description of the power tokens
    And the limitations that only one token can be stored
    And that it can only be used once per turn
    """
    lines = [
        "Complete a box → earn 1 token",
        "(max 1 stored). Use a token",
        "once per turn.",
    ]
    y = panel_rect.y - 10

    for txt in lines:
        surf = TOKEN_FONT.render(txt, True, Colors.BLACK)
        surface.blit(surf, (panel_rect.x + 10, y))
        y += surf.get_height() + 5


def draw_board(win, game: DotsAndBoxesGame, grid_size):
    """
    This function draws the game board
    It draws the dots, lines, and boxes on the screen
    It also draws the buttons, information and score info
    """
    spacing = min(
        (SCREEN_WIDTH - 2 * MARGIN) // (grid_size - 1),
        (SCREEN_HEIGHT - 2 * MARGIN) // (grid_size - 1),
    )
    bw, bh = spacing * (grid_size - 1), spacing * (grid_size - 1)
    ox = (SCREEN_WIDTH - bw) // 2
    oy = (SCREEN_HEIGHT - bh) // 2

    win.fill(Colors.WHITE)

    # This loop draws the dots
    for ry in range(grid_size):
        for cx in range(grid_size):
            pygame.draw.circle(
                win, Colors.BLACK, (ox + cx * spacing, oy + ry * spacing), DOT_RADIUS
            )

    # This loop draws the lines
    for mv, owner in game.lines.items():
        x1, y1, x2, y2 = mv
        col = (
            Colors.PLAYER_LINE_COLOR if owner == Player.PLAYER else Colors.AI_LINE_COLOR
        )  # Different colors of lines for player and AI
        start = (ox + x1 * spacing, oy + y1 * spacing)
        end = (ox + x2 * spacing, oy + y2 * spacing)
        pygame.draw.line(win, col, start, end, LINE_WIDTH)

    # This loop draws the boxes
    for bx, owner in game.boxes.items():
        x, y = bx
        rect = pygame.Rect(
            ox + x * spacing + LINE_WIDTH,
            oy + y * spacing + LINE_WIDTH,
            spacing - 2 * LINE_WIDTH,
            spacing - 2 * LINE_WIDTH,
        )
        color = Colors.PINK if owner == Player.PLAYER else Colors.BLUE

        pygame.draw.rect(win, color, rect)

    back = pygame.Rect(20, 20, *BUTTON_BACK_SIZE)
    quitb = pygame.Rect(SCREEN_WIDTH - 220, 20, 200, 50)

    draw_text_button(win, "Back to Menu", back)
    draw_text_button(win, "Quit", quitb)

    left_pan = pygame.Rect(20, oy, 240, bh)
    right_pan = pygame.Rect(SCREEN_WIDTH - 260, oy, 240, bh)
    info_pan = pygame.Rect(SCREEN_WIDTH - 260, oy + bh + 20, 240, 60)

    power_btns = draw_power_panel(win, left_pan)
    draw_score_panel(win, game, right_pan)
    draw_info_panel(win, info_pan)

    pygame.display.update()

    return back, quitb, spacing, (ox, oy), power_btns


def confirm_dialog(msg):
    """
    This function displays a confirmation dialog
    It asks the user to confirm their action"""
    w, h = CONFIRM_DIALOG_SIZE
    r = pygame.Rect((SCREEN_WIDTH - w) // 2, (SCREEN_HEIGHT - h) // 2, w, h)
    yes = pygame.Rect(r.x + 60, r.bottom - 100, 140, 60)
    no = pygame.Rect(r.right - 200, r.bottom - 100, 140, 60)

    while True:
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        ov.set_alpha(180)
        ov.fill(Colors.GRAY)
        screen.blit(ov, (0, 0))
        pygame.draw.rect(screen, Colors.BUTTON_COLOR, r, border_radius=10)

        p = FONT.render(msg, True, Colors.WHITE)

        screen.blit(p, p.get_rect(center=(r.centerx, r.y + 80)))
        draw_text_button(screen, "Yes", yes, yes.collidepoint(pygame.mouse.get_pos()))
        draw_text_button(screen, "No", no, no.collidepoint(pygame.mouse.get_pos()))

        pygame.display.update()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.MOUSEBUTTONDOWN:
                if yes.collidepoint(e.pos):
                    return True
                if no.collidepoint(e.pos):
                    return False


def end_game_menu(grid_size, game: DotsAndBoxesGame, difficulty, algo_choice):
    """
    This function displays the end game menu
    Also displays the result of the game
    """
    res = game.evaluate()
    outcome = "You win!" if res < 0 else "You lose!" if res > 0 else "Tie game!"
    pb = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 300, 60)
    mb = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 80, 300, 60)
    qb = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 160, 300, 60)
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    overlay.fill((100, 100, 100, 180))
    screen.blit(overlay, (0, 0))

    while True:
        t = FONT.render(outcome, True, Colors.BLACK)

        screen.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)))
        draw_text_button(
            screen, "Play Again", pb, pb.collidepoint(pygame.mouse.get_pos())
        )
        draw_text_button(
            screen, "Main Menu", mb, mb.collidepoint(pygame.mouse.get_pos())
        )
        draw_text_button(screen, "Quit", qb, qb.collidepoint(pygame.mouse.get_pos()))

        pygame.display.update()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.MOUSEBUTTONDOWN:
                if pb.collidepoint(e.pos):
                    game_loop(grid_size, difficulty, algo_choice)
                    return
                if mb.collidepoint(e.pos):
                    return
                if qb.collidepoint(e.pos):
                    pygame.quit()
                    sys.exit()


def game_loop(grid_size, difficulty, algo_choice):
    """
    This function runs the main game loop
    It handles the game logic and user input
    It also updates the game state and draws the game board
    """
    depth_map = {
        "Easy": 1,
        "Medium": 2,
        "Hard": 3,
    }  # This maps the difficulty of the AI by limiting the depth of the minimax algorithm
    ai_depth = depth_map.get(difficulty, 2)
    ai_prob = {"Easy": 0.1, "Medium": 0.3, "Hard": 0.5}.get(
        difficulty, 0.3
    )  # This is the probability of AI using the power token according to the difficulty level
    clock = pygame.time.Clock()
    game = DotsAndBoxesGame(grid_size)
    game.current_player = random.choice(
        [Player.PLAYER, Player.AI]
    )  # Make sure that the first move is random
    extra_move = False
    swap_count = 0

    while True:
        clock.tick(FPS)
        back_btn, quit_btn, spacing, offset, power_btns = draw_board(
            screen, game, grid_size
        )

        # Check if all the lines are drawn in the grid
        if game.is_terminal():
            end_game_menu(grid_size, game, difficulty, algo_choice)
            return

        # AI's move
        if game.current_player == Player.AI:
            base_eval, _ = (
                (alpha_beta if algo_choice == "alpha-beta" else minimax)(
                    game,
                    ai_depth,
                    alpha=-float("inf"),
                    beta=float("inf"),
                    maximizing=True,
                )
                if algo_choice == "alpha-beta"
                else minimax(game, ai_depth, True)
            )

            best_eval = base_eval
            best_action = None  # Here None means no token should be used

            if (
                game.power_tokens[Player.AI] >= 1
                and not game.power_used_this_turn
                and random.random() < ai_prob
            ):
                # Try each of the three power-ups
                for action in ("Extra Move", "Line Reversal", "Swap Token"):
                    ng = game.clone()

                    if action == "Line Reversal":
                        if ng.last_move and ng.lines.get(ng.last_move) != Player.AI:
                            del ng.lines[ng.last_move]
                            ng.power_tokens[Player.AI] -= 1
                            ng.power_used_this_turn = True
                            extra_move = False

                    elif action == "Extra Move":
                        extra_move = True
                        ng.power_tokens[Player.AI] -= 1
                        ng.power_used_this_turn = True
                    elif action == "Swap Token":
                        extra_move = False
                        for _ in range(2):
                            choices = ng.get_possible_moves()
                            if not choices:
                                break
                            rm = random.choice(choices)
                            ng.make_move(rm)
                        ng.power_tokens[Player.AI] -= 1
                        ng.power_used_this_turn = True
                    else:
                        continue

                    if algo_choice == "alpha-beta":
                        val, _ = alpha_beta(
                            ng, ai_depth, -float("inf"), float("inf"), True
                        )
                    else:
                        val, _ = minimax(ng, ai_depth, True)

                    if val > best_eval:
                        best_eval = val
                        best_action = action

            if best_action is not None:
                game.power_used_this_turn = True

                if best_action == "Extra Move":
                    extra_move = True
                elif best_action == "Line Reversal" and game.last_move:
                    del game.lines[game.last_move]
                elif best_action == "Swap Token":
                    swap_count = 2

            if algo_choice == "alpha-beta":
                _, best_move = alpha_beta(
                    game, ai_depth, -float("inf"), float("inf"), True
                )
            else:
                _, best_move = minimax(game, ai_depth, True)

            if best_move:
                game.make_move(best_move)

            if extra_move:
                game.current_player = Player.AI
                extra_move = False

            continue

        # Player's move
        for e in pygame.event.get():
            if e.type == pygame.QUIT and confirm_dialog("Quit the game?"):
                pygame.quit()
                sys.exit()

            if e.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(e.pos) and confirm_dialog(
                    "Back to main menu?"
                ):
                    return

                if quit_btn.collidepoint(e.pos) and confirm_dialog("Quit the game?"):
                    pygame.quit()
                    sys.exit()

                for act, rect in power_btns.items():
                    if (
                        rect.collidepoint(e.pos)
                        and game.power_tokens[Player.PLAYER] >= 1
                        and not game.power_used_this_turn
                    ):
                        if act == "Line Reversal":
                            if (
                                game.last_move
                                and game.lines.get(game.last_move) != Player.PLAYER
                            ):
                                del game.lines[game.last_move]
                                game.power_tokens[Player.PLAYER] = 0
                                game.power_used_this_turn = True
                            else:
                                err_msg = FONT.render(
                                    "No valid line to reverse", True, Colors.RED
                                )
                                screen.blit(
                                    err_msg,
                                    (
                                        SCREEN_WIDTH // 2 - err_msg.get_width() // 2,
                                        SCREEN_HEIGHT // 2 - err_msg.get_height() // 2,
                                    ),
                                )
                                pygame.display.update()
                                pygame.time.delay(2000)

                        if act == "Extra Move":
                            extra_move = True
                            game.power_tokens[Player.PLAYER] = 0
                            game.power_used_this_turn = True

                        elif act == "Swap Token":
                            swap_count = 2
                            game.power_tokens[Player.PLAYER] = 0
                            game.power_used_this_turn = True

                        break

                mv = get_line_from_mouse(e.pos, grid_size, spacing, game.lines, offset)

                if mv:
                    game.make_move(mv)

                    if extra_move:
                        game.current_player = Player.PLAYER
                        extra_move = False

                    if swap_count > 0:
                        swap_count -= 1
                        avail = game.get_possible_moves()
                        m2 = random.choice(avail)
                        game.make_move(m2)
                        game.current_player = Player.PLAYER

        pygame.display.update()


def grid_size_menu(difficulty):
    """
    This function displays a menu for the user to select the grid size
    Provide with predefined options and allow them to enter a custom size as well
    """
    clock = pygame.time.Clock()
    txt = ""

    while True:
        screen.fill(Colors.GRAY)
        mx, my = pygame.mouse.get_pos()
        title = FONT.render(f"{difficulty} - Choose Grid Size", True, Colors.BLACK)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

        b5 = pygame.Rect(SCREEN_WIDTH // 2 - 150, 150, 100, 50)
        b10 = pygame.Rect(SCREEN_WIDTH // 2 + 60, 150, 100, 50)
        b15 = pygame.Rect(SCREEN_WIDTH // 2 - 45, 220, 100, 50)

        draw_text_button(screen, "5", b5, b5.collidepoint(mx, my))
        draw_text_button(screen, "10", b10, b10.collidepoint(mx, my))
        draw_text_button(screen, "15", b15, b15.collidepoint(mx, my))

        box = pygame.Rect(SCREEN_WIDTH // 2 - 75, 300, 150, 50)
        pygame.draw.rect(screen, Colors.WHITE, box)

        lbl = FONT.render(txt, True, Colors.BLACK)
        screen.blit(lbl, (box.x + 10, box.y + 10))

        pygame.draw.rect(screen, Colors.BLACK, box, 2)
        allowed = FONT.render("Allowed: 3-20", True, Colors.BLACK)
        screen.blit(allowed, (SCREEN_WIDTH // 2 - allowed.get_width() // 2, 360))

        sub = pygame.Rect(SCREEN_WIDTH // 2 - 75, 400, 150, 50)
        draw_text_button(screen, "Submit", sub, sub.collidepoint(mx, my))

        bb = pygame.Rect(20, SCREEN_HEIGHT - 70, 150, 50)
        qb = pygame.Rect(SCREEN_WIDTH - 170, SCREEN_HEIGHT - 70, 150, 50)

        draw_text_button(screen, "Back", bb, bb.collidepoint(mx, my))
        draw_text_button(screen, "Quit", qb, qb.collidepoint(mx, my))

        pygame.display.update()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_BACKSPACE:
                    txt = txt[:-1]
                elif e.unicode.isdigit() and len(txt) < 2:
                    txt += e.unicode

            if e.type == pygame.MOUSEBUTTONDOWN:
                if bb.collidepoint(e.pos):
                    return None
                if qb.collidepoint(e.pos):
                    pygame.quit()
                    sys.exit()
                if b5.collidepoint(e.pos):
                    return 5
                if b10.collidepoint(e.pos):
                    return 10
                if b15.collidepoint(e.pos):
                    return 15
                if sub.collidepoint(e.pos) and txt:
                    val = int(txt)
                    if 3 <= val <= 20:
                        return val
                    txt = ""

        clock.tick(FPS)


def main_menu():
    """
    This function displays the main menu of the game
    Which allows the user to select the difficulty level
    And the grid size for the game
    """
    clock = pygame.time.Clock()
    diffs = ["Easy", "Medium", "Hard"]  # Difficulties

    while True:
        screen.fill(Colors.GRAY)  # For the background color
        mx, my = pygame.mouse.get_pos()  # Get mouse position
        title = FONT.render("Select Difficulty", True, Colors.BLACK)

        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        btns = []

        for i, d in enumerate(diffs):
            r = pygame.Rect(SCREEN_WIDTH // 2 - 150, 150 + i * 70, 300, 60)
            btns.append((r, d))
            draw_text_button(screen, d, r, r.collidepoint(mx, my))

        # Quit button
        qb = pygame.Rect(SCREEN_WIDTH // 2 - 150, 150 + len(diffs) * 70, 300, 60)
        draw_text_button(screen, "Quit", qb, qb.collidepoint(mx, my))
        pygame.display.update()

        for e in pygame.event.get():
            # If the user closes the window, exit the game (this avoids the unnecessary crash which we figured out was happening when the game ended)
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.MOUSEBUTTONDOWN:
                for r, d in btns:
                    if r.collidepoint(e.pos):
                        # Get the grid size from user (predefined options, as well as custom input)
                        sz = grid_size_menu(d)

                        if sz:
                            if d == "Easy":
                                algo = "minimax"
                            else:
                                algo = "alpha-beta"

                            # Start the game
                            game_loop(sz, d, algo)

                # Quit if the user clicks on quit
                if qb.collidepoint(e.pos):
                    pygame.quit()
                    sys.exit()

        clock.tick(FPS)


if __name__ == "__main__":
    main_menu()
