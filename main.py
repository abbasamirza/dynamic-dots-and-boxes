import pygame
from logic import DotsAndBoxesGame
from minimax import minimax
from constants import Player

pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (255, 182, 193)
BLUE = (173, 216, 230)
GRAY = (200, 200, 200)
BUTTON_COLOR = (100, 100, 255)
BUTTON_HOVER = (150, 150, 255)

FPS = 60
LINE_WIDTH = 4
DOT_RADIUS = 6
MARGIN = 80

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
FONT = pygame.font.SysFont("Arial", 36)


def draw_text_button(surface, text, rect, hover=False):
    color = BUTTON_HOVER if hover else BUTTON_COLOR
    pygame.draw.rect(surface, color, rect, border_radius=10)
    label = FONT.render(text, True, WHITE)
    label_rect = label.get_rect(center=rect.center)
    surface.blit(label, label_rect)


def get_line_from_mouse(pos, grid_size, spacing):
    x, y = pos
    closest = None
    min_dist = float("inf")

    for row in range(grid_size):
        for col in range(grid_size - 1):
            # horizontal
            x1 = MARGIN + col * spacing
            y1 = MARGIN + row * spacing
            x2 = MARGIN + (col + 1) * spacing
            y2 = y1
            mid = ((x1 + x2) / 2, y1)
            dist = ((x - mid[0]) ** 2 + (y - mid[1]) ** 2) ** 0.5
            if dist < 15 and dist < min_dist:
                closest = (col, row, col + 1, row)
                min_dist = dist

    for row in range(grid_size - 1):
        for col in range(grid_size):
            # vertical
            x1 = MARGIN + col * spacing
            y1 = MARGIN + row * spacing
            x2 = x1
            y2 = MARGIN + (row + 1) * spacing
            mid = (x1, (y1 + y2) / 2)
            dist = ((x - mid[0]) ** 2 + (y - mid[1]) ** 2) ** 0.5
            if dist < 15 and dist < min_dist:
                closest = (col, row, col, row + 1)
                min_dist = dist

    return closest


def draw_board(win, game, grid_size):
    win.fill(WHITE)
    spacing = (SCREEN_WIDTH - 2 * MARGIN) // (grid_size - 1)

    for y in range(grid_size):
        for x in range(grid_size):
            pygame.draw.circle(
                win, BLACK, (MARGIN + x * spacing, MARGIN + y * spacing), DOT_RADIUS
            )

    for line in game.lines:
        x1, y1, x2, y2 = line
        pygame.draw.line(
            win,
            BLACK,
            (MARGIN + x1 * spacing, MARGIN + y1 * spacing),
            (MARGIN + x2 * spacing, MARGIN + y2 * spacing),
            LINE_WIDTH,
        )

    for box, owner in game.boxes.items():
        x, y = box
        rect = pygame.Rect(
            MARGIN + x * spacing + LINE_WIDTH,
            MARGIN + y * spacing + LINE_WIDTH,
            spacing - 2 * LINE_WIDTH,
            spacing - 2 * LINE_WIDTH,
        )
        color = PINK if owner == Player.PLAYER else BLUE
        pygame.draw.rect(win, color, rect)

    # Buttons
    back_button = pygame.Rect(20, 20, 200, 50)
    quit_button = pygame.Rect(SCREEN_WIDTH - 220, 20, 200, 50)
    draw_text_button(win, "Back to Menu", back_button)
    draw_text_button(win, "Quit", quit_button)

    pygame.display.update()
    return back_button, quit_button


def game_loop(grid_size):
    clock = pygame.time.Clock()
    game = DotsAndBoxesGame(grid_size)
    spacing = (SCREEN_WIDTH - 2 * MARGIN) // (grid_size - 1)
    run = True

    while run:
        clock.tick(FPS)
        back_button, quit_button = draw_board(screen, game, grid_size)

        if game.current_player == Player.AI:
            best_move = minimax(game, 2, True)[1]
            if best_move:
                game.make_move(best_move)
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return  # go back to menu
                if quit_button.collidepoint(event.pos):
                    pygame.quit()
                    exit()
                move = get_line_from_mouse(event.pos, grid_size, spacing)
                if move and move not in game.lines:
                    game.make_move(move)


def main_menu():
    clock = pygame.time.Clock()
    while True:
        screen.fill(GRAY)
        mx, my = pygame.mouse.get_pos()

        easy_button = pygame.Rect(SCREEN_WIDTH // 2 - 150, 200, 300, 60)
        medium_button = pygame.Rect(SCREEN_WIDTH // 2 - 150, 300, 300, 60)
        hard_button = pygame.Rect(SCREEN_WIDTH // 2 - 150, 400, 300, 60)
        quit_button = pygame.Rect(SCREEN_WIDTH // 2 - 150, 500, 300, 60)

        draw_text_button(
            screen, "Easy (5x5)", easy_button, easy_button.collidepoint(mx, my)
        )
        draw_text_button(
            screen, "Medium (10x10)", medium_button, medium_button.collidepoint(mx, my)
        )
        draw_text_button(
            screen, "Hard (15x15)", hard_button, hard_button.collidepoint(mx, my)
        )
        draw_text_button(screen, "Quit", quit_button, quit_button.collidepoint(mx, my))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if easy_button.collidepoint(event.pos):
                    game_loop(5)
                if medium_button.collidepoint(event.pos):
                    game_loop(10)
                if hard_button.collidepoint(event.pos):
                    game_loop(15)
                if quit_button.collidepoint(event.pos):
                    pygame.quit()
                    exit()

            clock.tick(FPS)


if __name__ == "__main__":
    main_menu()
