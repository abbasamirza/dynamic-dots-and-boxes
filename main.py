import pygame, sys, math, random
from logic import DotsAndBoxesGame
from minimax import minimax
from constants import Player, Colors, BUTTON_BACK_SIZE, CONFIRM_DIALOG_SIZE

pygame.init()

FPS = 60
LINE_WIDTH = 4
DOT_RADIUS = 6
MARGIN = 80

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
FONT = pygame.font.SysFont("Arial", 36)


def distance_point_to_segment(point, seg_start, seg_end):
    (x, y) = point
    (x1, y1) = seg_start
    (x2, y2) = seg_end
    dx = x2 - x1
    dy = y2 - y1
    if dx == dy == 0:
        return math.hypot(x - x1, y - y1)
    t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return math.hypot(x - proj_x, y - proj_y)


def draw_text_button(surface, text, rect, hover=False):
    color = Colors.BUTTON_HOVER if hover else Colors.BUTTON_COLOR
    pygame.draw.rect(surface, color, rect, border_radius=10)
    label = FONT.render(text, True, Colors.WHITE)
    label_rect = label.get_rect(center=rect.center)
    surface.blit(label, label_rect)


def get_line_from_mouse(pos, grid_size, spacing, drawn_lines, offset):
    offset_x, offset_y = offset
    x, y = pos
    candidates = []
    for row in range(grid_size):
        for col in range(grid_size - 1):
            start = (offset_x + col * spacing, offset_y + row * spacing)
            end = (offset_x + (col + 1) * spacing, offset_y + row * spacing)
            move = (col, row, col + 1, row)
            if move in drawn_lines:
                continue
            dist = distance_point_to_segment(pos, start, end)
            candidates.append((dist, move))
    for row in range(grid_size - 1):
        for col in range(grid_size):
            start = (offset_x + col * spacing, offset_y + row * spacing)
            end = (offset_x + col * spacing, offset_y + (row + 1) * spacing)
            move = (col, row, col, row + 1)
            if move in drawn_lines:
                continue
            dist = distance_point_to_segment(pos, start, end)
            candidates.append((dist, move))
    if candidates:
        best = min(candidates, key=lambda x: x[0])
        if best[0] < 20:
            return best[1]
    return None


def draw_board(win, game, grid_size):
    spacing = min(
        (SCREEN_WIDTH - 2 * MARGIN) // (grid_size - 1),
        (SCREEN_HEIGHT - 2 * MARGIN) // (grid_size - 1),
    )
    board_width = spacing * (grid_size - 1)
    board_height = spacing * (grid_size - 1)
    offset_x = (SCREEN_WIDTH - board_width) // 2
    offset_y = (SCREEN_HEIGHT - board_height) // 2
    win.fill(Colors.WHITE)
    for y in range(grid_size):
        for x in range(grid_size):
            pygame.draw.circle(
                win,
                Colors.BLACK,
                (offset_x + x * spacing, offset_y + y * spacing),
                DOT_RADIUS,
            )
    for move, owner in game.lines.items():
        x1, y1, x2, y2 = move
        color = (
            Colors.PLAYER_LINE_COLOR if owner == Player.PLAYER else Colors.AI_LINE_COLOR
        )
        start = (offset_x + x1 * spacing, offset_y + y1 * spacing)
        end = (offset_x + x2 * spacing, offset_y + y2 * spacing)
        pygame.draw.line(win, color, start, end, LINE_WIDTH)
    for box, owner in game.boxes.items():
        x, y = box
        rect = pygame.Rect(
            offset_x + x * spacing + LINE_WIDTH,
            offset_y + y * spacing + LINE_WIDTH,
            spacing - 2 * LINE_WIDTH,
            spacing - 2 * LINE_WIDTH,
        )
        color = Colors.PINK if owner == Player.PLAYER else Colors.BLUE
        pygame.draw.rect(win, color, rect)
    back_button = pygame.Rect(20, 20, BUTTON_BACK_SIZE[0], BUTTON_BACK_SIZE[1])
    quit_button = pygame.Rect(SCREEN_WIDTH - 220, 20, 200, 50)
    draw_text_button(win, "Back to Menu", back_button)
    draw_text_button(win, "Quit", quit_button)
    pygame.display.update()
    return back_button, quit_button, spacing, (offset_x, offset_y)


def confirm_dialog(message):
    dialog_width, dialog_height = CONFIRM_DIALOG_SIZE
    dialog_rect = pygame.Rect(
        (SCREEN_WIDTH - dialog_width) // 2,
        (SCREEN_HEIGHT - dialog_height) // 2,
        dialog_width,
        dialog_height,
    )
    yes_button = pygame.Rect(
        dialog_rect.x + 60, dialog_rect.y + dialog_height - 100, 140, 60
    )
    no_button = pygame.Rect(
        dialog_rect.x + dialog_width - 200, dialog_rect.y + dialog_height - 100, 140, 60
    )
    while True:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(Colors.GRAY)
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, Colors.BUTTON_COLOR, dialog_rect, border_radius=10)
        prompt = FONT.render(message, True, Colors.WHITE)
        prompt_rect = prompt.get_rect(center=(dialog_rect.centerx, dialog_rect.y + 80))
        screen.blit(prompt, prompt_rect)
        draw_text_button(
            screen, "Yes", yes_button, yes_button.collidepoint(pygame.mouse.get_pos())
        )
        draw_text_button(
            screen, "No", no_button, no_button.collidepoint(pygame.mouse.get_pos())
        )
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if yes_button.collidepoint(event.pos):
                    return True
                if no_button.collidepoint(event.pos):
                    return False


def end_game_menu(grid_size, game, difficulty):
    result = game.evaluate()
    if result < 0:
        outcome = "You win!"
    elif result > 0:
        outcome = "You lose!"
    else:
        outcome = "Tie game!"
    play_button = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 300, 60)
    menu_button = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 80, 300, 60)
    quit_button = pygame.Rect(
        SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 160, 300, 60
    )

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((100, 100, 100, 180))
    screen.blit(overlay, (0, 0))
    while True:
        result_text = FONT.render(outcome, True, Colors.BLACK)
        result_rect = result_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)
        )
        screen.blit(result_text, result_rect)
        draw_text_button(
            screen,
            "Play Again",
            play_button,
            play_button.collidepoint(pygame.mouse.get_pos()),
        )
        draw_text_button(
            screen,
            "Main Menu",
            menu_button,
            menu_button.collidepoint(pygame.mouse.get_pos()),
        )
        draw_text_button(
            screen,
            "Quit",
            quit_button,
            quit_button.collidepoint(pygame.mouse.get_pos()),
        )
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    game_loop(grid_size, difficulty)
                    return
                if menu_button.collidepoint(event.pos):
                    return
                if quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()


def game_loop(grid_size, difficulty):
    depth_mapping = {"Easy": 1, "Medium": 2, "Hard": 3}
    ai_depth = depth_mapping.get(difficulty, 2)
    clock = pygame.time.Clock()
    game = DotsAndBoxesGame(grid_size)
    game.current_player = random.choice([Player.PLAYER, Player.AI])
    while True:
        clock.tick(FPS)
        back_btn, quit_btn, spacing, offset = draw_board(screen, game, grid_size)
        if game.is_terminal():
            end_game_menu(grid_size, game, difficulty)
            return
        if game.current_player == Player.AI:
            best_move = minimax(game, ai_depth, True)[1]
            if best_move:
                game.make_move(best_move)
            continue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if confirm_dialog("Quit the game?"):
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(event.pos):
                    if confirm_dialog("Go back to main menu?"):
                        return
                if quit_btn.collidepoint(event.pos):
                    if confirm_dialog("Quit the game?"):
                        pygame.quit()
                        sys.exit()
                move = get_line_from_mouse(
                    event.pos, grid_size, spacing, game.lines, offset
                )
                if move:
                    game.make_move(move)
        pygame.display.update()


def grid_size_menu(difficulty):
    clock = pygame.time.Clock()
    input_text = ""
    while True:
        screen.fill(Colors.GRAY)
        mx, my = pygame.mouse.get_pos()
        title = FONT.render(f"{difficulty} - Choose Grid Size", True, Colors.BLACK)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        btn_5 = pygame.Rect(SCREEN_WIDTH // 2 - 150, 150, 100, 50)
        btn_10 = pygame.Rect(SCREEN_WIDTH // 2 + 60, 150, 100, 50)
        btn_15 = pygame.Rect(SCREEN_WIDTH // 2 - 45, 220, 100, 50)
        draw_text_button(screen, "5", btn_5, btn_5.collidepoint(mx, my))
        draw_text_button(screen, "10", btn_10, btn_10.collidepoint(mx, my))
        draw_text_button(screen, "15", btn_15, btn_15.collidepoint(mx, my))
        custom_box = pygame.Rect(SCREEN_WIDTH // 2 - 75, 300, 150, 50)
        pygame.draw.rect(screen, Colors.WHITE, custom_box)
        custom_label = FONT.render(input_text, True, Colors.BLACK)
        screen.blit(custom_label, (custom_box.x + 10, custom_box.y + 10))
        pygame.draw.rect(screen, Colors.BLACK, custom_box, 2)
        allowed_text = FONT.render("Allowed: 3-20", True, Colors.BLACK)
        screen.blit(
            allowed_text, (SCREEN_WIDTH // 2 - allowed_text.get_width() // 2, 360)
        )
        submit_box = pygame.Rect(SCREEN_WIDTH // 2 - 75, 400, 150, 50)
        draw_text_button(screen, "Submit", submit_box, submit_box.collidepoint(mx, my))
        back_button = pygame.Rect(20, SCREEN_HEIGHT - 70, 150, 50)
        quit_button = pygame.Rect(SCREEN_WIDTH - 170, SCREEN_HEIGHT - 70, 150, 50)
        draw_text_button(screen, "Back", back_button, back_button.collidepoint(mx, my))
        draw_text_button(screen, "Quit", quit_button, quit_button.collidepoint(mx, my))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.unicode.isdigit() and len(input_text) < 2:
                    input_text += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return None
                if quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
                if btn_5.collidepoint(event.pos):
                    return 5
                if btn_10.collidepoint(event.pos):
                    return 10
                if btn_15.collidepoint(event.pos):
                    return 15
                if submit_box.collidepoint(event.pos) and input_text != "":
                    size = int(input_text)
                    if 3 <= size <= 20:
                        return size
                    else:
                        input_text = ""
        clock.tick(FPS)


def main_menu():
    clock = pygame.time.Clock()
    difficulties = ["Easy", "Medium", "Hard"]
    while True:
        screen.fill(Colors.GRAY)
        mx, my = pygame.mouse.get_pos()
        title = FONT.render("Select Difficulty", True, Colors.BLACK)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        buttons = []
        for i, diff in enumerate(difficulties):
            rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 150 + i * 70, 300, 60)
            buttons.append((rect, diff))
            draw_text_button(screen, diff, rect, rect.collidepoint(mx, my))
        quit_button = pygame.Rect(
            SCREEN_WIDTH // 2 - 150, 150 + len(difficulties) * 70, 300, 60
        )
        draw_text_button(screen, "Quit", quit_button, quit_button.collidepoint(mx, my))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for rect, diff in buttons:
                    if rect.collidepoint(event.pos):
                        grid_size = grid_size_menu(diff)
                        if grid_size:
                            game_loop(grid_size, diff)
                if quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
        clock.tick(FPS)


if __name__ == "__main__":
    main_menu()
