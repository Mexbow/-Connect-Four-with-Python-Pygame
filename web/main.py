# Connect Four - browser build (pygbag / WebAssembly)
# Single-file version of GUI.py + lvl.py + easy/medium/hard.py:
# Tkinter menus are replaced with Pygame screens and the main loop is async,
# which is required for running in the browser.
import asyncio
import math
import random

import pygame

BLUE = (30, 125, 240)
BOARD_BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 129, 100)
LIGHT_YELLOW = (236, 231, 95)

ROW_COUNT = 6
COLUMN_COUNT = 7
WINDOW_LENGTH = 4

PLAYER = 0
AI = 1
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

SQUARESIZE = 100
WIDTH = COLUMN_COUNT * SQUARESIZE
HEIGHT = (ROW_COUNT + 1) * SQUARESIZE
RADIUS = int(SQUARESIZE / 2 - 5)

# name -> (minimax depth, random first turn)  (same as easy.py / medium.py / hard.py)
LEVELS = {"Easy": (1, True), "Medium": (3, True), "Hard": (6, False)}


# ---------------------------------------------------------------- game logic
def create_board():
    return [[EMPTY] * COLUMN_COUNT for _ in range(ROW_COUNT)]


def copy_board(board):
    return [row[:] for row in board]


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == EMPTY


def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == EMPTY:
            return r


def get_valid_locations(board):
    return [c for c in range(COLUMN_COUNT) if is_valid_location(board, c)]


def winning_move(board, piece):
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if all(board[r][c + i] == piece for i in range(4)):
                return True
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return True
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True
    return False


def evaluate_window(window, piece):
    score = 0
    opp_piece = AI_PIECE if piece == PLAYER_PIECE else PLAYER_PIECE
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4
    return score


def score_position(board, piece):
    score = [board[r][COLUMN_COUNT // 2] for r in range(ROW_COUNT)].count(piece) * 3
    for r in range(ROW_COUNT):
        row = board[r]
        for c in range(COLUMN_COUNT - 3):
            score += evaluate_window(row[c:c + WINDOW_LENGTH], piece)
    for c in range(COLUMN_COUNT):
        col = [board[r][c] for r in range(ROW_COUNT)]
        for r in range(ROW_COUNT - 3):
            score += evaluate_window(col[r:r + WINDOW_LENGTH], piece)
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            score += evaluate_window([board[r + i][c + i] for i in range(WINDOW_LENGTH)], piece)
            score += evaluate_window([board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)], piece)
    return score


def is_terminal_node(board):
    return (winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE)
            or len(get_valid_locations(board)) == 0)


def minimax(board, depth, alpha, beta, maximizing):
    valid_locations = get_valid_locations(board)
    if winning_move(board, AI_PIECE):
        return None, 100000000000000
    if winning_move(board, PLAYER_PIECE):
        return None, -10000000000000
    if not valid_locations:
        return None, 0
    if depth == 0:
        return None, score_position(board, AI_PIECE)

    column = random.choice(valid_locations)
    if maximizing:
        value = -math.inf
        for col in valid_locations:
            b = copy_board(board)
            drop_piece(b, get_next_open_row(b, col), col, AI_PIECE)
            new_score = minimax(b, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value, column = new_score, col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
    else:
        value = math.inf
        for col in valid_locations:
            b = copy_board(board)
            drop_piece(b, get_next_open_row(b, col), col, PLAYER_PIECE)
            new_score = minimax(b, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value, column = new_score, col
            beta = min(beta, value)
            if alpha >= beta:
                break
    return column, value


# ---------------------------------------------------------------- drawing
class Button:
    def __init__(self, text, center, color, font):
        self.text, self.color, self.font = text, color, font
        self.rect = pygame.Rect(0, 0, 260, 80)
        self.rect.center = center

    def draw(self, screen, mouse):
        color = tuple(min(255, v + 25) for v in self.color) if self.rect.collidepoint(mouse) else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        pygame.draw.rect(screen, WHITE, self.rect, 4, border_radius=12)
        label = self.font.render(self.text, True, WHITE)
        screen.blit(label, label.get_rect(center=self.rect.center))

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)


def draw_board(screen, board):
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BOARD_BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (c * SQUARESIZE + SQUARESIZE // 2, r * SQUARESIZE + SQUARESIZE + SQUARESIZE // 2), RADIUS)
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] != EMPTY:
                color = RED if board[r][c] == PLAYER_PIECE else YELLOW
                pygame.draw.circle(screen, color, (c * SQUARESIZE + SQUARESIZE // 2, HEIGHT - (r * SQUARESIZE + SQUARESIZE // 2)), RADIUS)


def draw_title(screen, font, text):
    screen.fill(BLUE)
    label = font.render(text, True, WHITE)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, 140)))


# ---------------------------------------------------------------- main loop
async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Connect Four")
    clock = pygame.time.Clock()

    title_font = pygame.font.Font(None, 110)
    button_font = pygame.font.Font(None, 56)
    msg_font = pygame.font.Font(None, 72)

    menu_buttons = [Button("Play", (WIDTH // 2, 380), ORANGE, button_font)]
    level_buttons = [Button(name, (WIDTH // 2, 300 + i * 110), ORANGE, button_font)
                     for i, name in enumerate(LEVELS)]
    back_button = Button("Back", (WIDTH // 2, 300 + 3 * 110), LIGHT_YELLOW, button_font)

    state = "menu"
    board = None
    depth = 1
    turn = PLAYER
    game_over = False
    message = None
    end_time = 0
    ai_ready_time = 0
    posx = WIDTH // 2

    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if state == "menu":
                if menu_buttons[0].clicked(event):
                    state = "levels"

            elif state == "levels":
                for b in level_buttons:
                    if b.clicked(event):
                        depth, random_start = LEVELS[b.text]
                        board = create_board()
                        turn = random.randint(PLAYER, AI) if random_start else PLAYER
                        ai_ready_time = pygame.time.get_ticks() + 500
                        game_over, message = False, None
                        state = "game"
                if back_button.clicked(event):
                    state = "menu"

            elif state == "game":
                if event.type == pygame.MOUSEMOTION:
                    posx = event.pos[0]
                if event.type == pygame.MOUSEBUTTONDOWN and turn == PLAYER and not game_over:
                    col = min(COLUMN_COUNT - 1, event.pos[0] // SQUARESIZE)
                    if is_valid_location(board, col):
                        drop_piece(board, get_next_open_row(board, col), col, PLAYER_PIECE)
                        if winning_move(board, PLAYER_PIECE):
                            game_over, message = True, ("You win!!", RED)
                        elif not get_valid_locations(board):
                            game_over, message = True, ("Draw!", WHITE)
                        turn = AI
                        ai_ready_time = pygame.time.get_ticks() + 300

        # ---- render
        if state == "menu":
            draw_title(screen, title_font, "Connect Four")
            for b in menu_buttons:
                b.draw(screen, mouse)

        elif state == "levels":
            draw_title(screen, title_font, "Select Level")
            for b in level_buttons + [back_button]:
                b.draw(screen, mouse)

        elif state == "game":
            draw_board(screen, board)
            if game_over:
                text, color = message
                label = msg_font.render(text, True, color)
                screen.blit(label, label.get_rect(center=(WIDTH // 2, SQUARESIZE // 2)))
            elif turn == PLAYER:
                pygame.draw.circle(screen, RED, (posx, SQUARESIZE // 2), RADIUS)
            else:
                label = button_font.render("Bot is thinking...", True, YELLOW)
                screen.blit(label, label.get_rect(center=(WIDTH // 2, SQUARESIZE // 2)))

        pygame.display.flip()
        await asyncio.sleep(0)  # hand control back to the browser every frame
        clock.tick(60)

        # ---- AI move (after the "thinking" frame has been shown)
        if state == "game" and turn == AI and not game_over and pygame.time.get_ticks() >= ai_ready_time:
            col, _ = minimax(board, depth, -math.inf, math.inf, True)
            if col is not None and is_valid_location(board, col):
                drop_piece(board, get_next_open_row(board, col), col, AI_PIECE)
                if winning_move(board, AI_PIECE):
                    game_over, message = True, ("Bot wins!!", YELLOW)
                elif not get_valid_locations(board):
                    game_over, message = True, ("Draw!", WHITE)
            turn = PLAYER

        # ---- after a finished game, return to the level menu (as the desktop version does)
        if state == "game" and game_over:
            if end_time == 0:
                end_time = pygame.time.get_ticks() + 3000
            elif pygame.time.get_ticks() >= end_time:
                end_time = 0
                state = "levels"


asyncio.run(main())
