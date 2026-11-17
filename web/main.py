# Connect Four - browser build (pygbag / WebAssembly)
# Single-file version of GUI.py + lvl.py + easy/medium/hard.py:
# Tkinter menus are replaced with Pygame screens and the main loop is async,
# which is required for running in the browser.
import asyncio
import math
import random

import pygame

# ---------------------------------------------------------------- constants
ROW_COUNT = 6
COLUMN_COUNT = 7
WINDOW_LENGTH = 4

PLAYER = 0
AI = 1
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

SQ = 90                                  # cell size
RADIUS = 37
WIDTH = 700
BX = (WIDTH - COLUMN_COUNT * SQ) // 2    # board left
BY = 160                                 # board top
BOARD_W = COLUMN_COUNT * SQ
BOARD_H = ROW_COUNT * SQ
HOVER_Y = 112                            # y of the preview piece above the board
HEIGHT = BY + BOARD_H + 110

# colours
BG_TOP = (18, 32, 72)
BG_BOTTOM = (8, 12, 30)
BOARD = (30, 100, 230)
BOARD_EDGE = (20, 70, 180)
WHITE = (245, 245, 250)
MUTED = (160, 175, 210)
RED = (235, 60, 60)
RED_DARK = (170, 30, 35)
YELLOW = (250, 210, 50)
YELLOW_DARK = (195, 150, 20)
ORANGE = (255, 129, 100)
GREEN = (70, 190, 120)
GREY = (90, 100, 130)

PIECE_COLORS = {PLAYER_PIECE: (RED, RED_DARK), AI_PIECE: (YELLOW, YELLOW_DARK)}

# name -> (minimax depth, random first turn, description)  (same as easy/medium/hard.py)
LEVELS = {
    "Easy": (1, True, "Bot looks 1 move ahead"),
    "Medium": (3, True, "Bot looks 3 moves ahead"),
    "Hard": (6, False, "Bot looks 6 moves ahead"),
}


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


def winning_cells(board, piece):
    """Return the 4 (row, col) cells of a win for `piece`, or None."""
    for dr, dc in ((0, 1), (1, 0), (1, 1), (-1, 1)):
        for r in range(ROW_COUNT):
            for c in range(COLUMN_COUNT):
                cells = [(r + i * dr, c + i * dc) for i in range(4)]
                if all(0 <= rr < ROW_COUNT and 0 <= cc < COLUMN_COUNT and board[rr][cc] == piece
                       for rr, cc in cells):
                    return cells
    return None


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


# ---------------------------------------------------------------- drawing helpers
def cell_center(row, col):
    return BX + col * SQ + SQ // 2, BY + (ROW_COUNT - 1 - row) * SQ + SQ // 2


def make_background():
    surf = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        t = y / HEIGHT
        color = [int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3)]
        pygame.draw.line(surf, color, (0, y), (WIDTH, y))
    return surf


def make_board_overlay():
    """Blue board with transparent holes, drawn on top of the pieces."""
    pad = 12
    surf = pygame.Surface((BOARD_W + pad * 2, BOARD_H + pad * 2), pygame.SRCALPHA)
    pygame.draw.rect(surf, BOARD_EDGE, surf.get_rect(), border_radius=22)
    pygame.draw.rect(surf, BOARD, surf.get_rect().inflate(-6, -6), border_radius=20)
    for r in range(ROW_COUNT):
        for c in range(COLUMN_COUNT):
            x, y = pad + c * SQ + SQ // 2, pad + r * SQ + SQ // 2
            pygame.draw.circle(surf, BOARD_EDGE, (x, y), RADIUS + 3)
            pygame.draw.circle(surf, (0, 0, 0, 0), (x, y), RADIUS)
    return surf, (BX - pad, BY - pad)


def draw_piece(screen, piece, center, radius=RADIUS):
    light, dark = PIECE_COLORS[piece]
    x, y = int(center[0]), int(center[1])
    pygame.draw.circle(screen, dark, (x, y), radius)
    pygame.draw.circle(screen, light, (x, y), int(radius * 0.82))
    pygame.draw.circle(screen, dark, (x, y), int(radius * 0.55), 3)
    pygame.draw.circle(screen, (255, 255, 255), (x - radius // 3, y - radius // 3), max(3, radius // 7))


def draw_text(screen, font, text, color, center, shadow=True):
    if shadow:
        s = font.render(text, True, (0, 0, 0))
        s.set_alpha(110)
        screen.blit(s, s.get_rect(center=(center[0] + 3, center[1] + 3)))
    label = font.render(text, True, color)
    screen.blit(label, label.get_rect(center=center))


class Button:
    def __init__(self, text, center, color, font, size=(260, 72), sub=None, sub_font=None):
        self.text, self.color, self.font = text, color, font
        self.sub, self.sub_font = sub, sub_font
        self.rect = pygame.Rect((0, 0), size)
        self.rect.center = center
        self.enabled = True

    def draw(self, screen, mouse):
        hover = self.enabled and self.rect.collidepoint(mouse)
        color = self.color if self.enabled else GREY
        if hover:
            color = tuple(min(255, v + 30) for v in color)
        rect = self.rect.move(0, -3 if hover else 0)
        pygame.draw.rect(screen, (0, 0, 0), self.rect.move(0, 6), border_radius=16)
        pygame.draw.rect(screen, color, rect, border_radius=16)
        pygame.draw.rect(screen, (255, 255, 255), rect, 3, border_radius=16)
        text_color = WHITE if self.enabled else MUTED
        if self.sub:
            draw_text(screen, self.font, self.text, text_color, (rect.centerx, rect.centery - 12), shadow=False)
            draw_text(screen, self.sub_font, self.sub, text_color, (rect.centerx, rect.centery + 20), shadow=False)
        else:
            draw_text(screen, self.font, self.text, text_color, rect.center, shadow=False)

    def clicked(self, event):
        return (self.enabled and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                and self.rect.collidepoint(event.pos))


# ---------------------------------------------------------------- game state
class Game:
    def __init__(self, level):
        self.level = level
        self.depth, random_start, _ = LEVELS[level]
        self.board = create_board()
        self.history = []          # list of (row, col, piece) - newest last
        self.turn = random.randint(PLAYER, AI) if random_start else PLAYER
        self.game_over = False
        self.message = None
        self.win_cells = None
        self.anim = None           # falling piece: dict(row, col, piece, y, vy, target)
        self.ai_ready_time = pygame.time.get_ticks() + 600

    @property
    def busy(self):
        return self.anim is not None or (self.turn == AI and not self.game_over)

    def start_drop(self, col, piece):
        row = get_next_open_row(self.board, col)
        self.anim = {"row": row, "col": col, "piece": piece, "y": float(HOVER_Y), "vy": 0.0,
                     "target": cell_center(row, col)[1]}

    def update_anim(self):
        a = self.anim
        if not a:
            return
        a["vy"] += 2.2
        a["y"] += a["vy"]
        if a["y"] >= a["target"]:
            self.anim = None
            self.place(a["row"], a["col"], a["piece"])

    def place(self, row, col, piece):
        drop_piece(self.board, row, col, piece)
        self.history.append((row, col, piece))
        cells = winning_cells(self.board, piece)
        if cells:
            self.game_over, self.win_cells = True, cells
            self.message = ("You win!", RED) if piece == PLAYER_PIECE else ("Bot wins!", YELLOW)
        elif not get_valid_locations(self.board):
            self.game_over, self.message = True, ("It's a draw!", WHITE)
        self.turn = AI if piece == PLAYER_PIECE else PLAYER
        self.ai_ready_time = pygame.time.get_ticks() + 350

    def last_move_text(self):
        if not self.history:
            return "No moves yet"
        parts = []
        for _, col, piece in self.history[-2:]:
            who = "You" if piece == PLAYER_PIECE else "Bot"
            parts.append(f"{who}: column {col + 1}")
        return "Last moves  -  " + "   |   ".join(parts)


# ---------------------------------------------------------------- main loop
async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Connect Four")
    clock = pygame.time.Clock()

    title_font = pygame.font.Font(None, 104)
    big_font = pygame.font.Font(None, 64)
    button_font = pygame.font.Font(None, 46)
    small_font = pygame.font.Font(None, 30)
    tiny_font = pygame.font.Font(None, 24)

    background = make_background()
    board_overlay, board_pos = make_board_overlay()

    play_button = Button("Play", (WIDTH // 2, 470), ORANGE, button_font)
    level_buttons = [Button(name, (WIDTH // 2, 300 + i * 110), ORANGE, button_font, (320, 90),
                            sub=desc, sub_font=tiny_font)
                     for i, (name, (_, _, desc)) in enumerate(LEVELS.items())]
    back_button = Button("Back", (WIDTH // 2, 300 + 3 * 110), GREY, button_font, (200, 64))
    bar_y = HEIGHT - 45
    restart_button = Button("New game", (WIDTH // 2 - 110, bar_y), ORANGE, small_font, (180, 52))
    menu_button = Button("Levels", (WIDTH // 2 + 110, bar_y), GREY, small_font, (180, 52))

    state = "menu"
    game = None
    posx = WIDTH // 2

    while True:
        mouse = pygame.mouse.get_pos()
        now = pygame.time.get_ticks()

        # ---- input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if state == "menu":
                if play_button.clicked(event):
                    state = "levels"

            elif state == "levels":
                for b in level_buttons:
                    if b.clicked(event):
                        game, state = Game(b.text), "game"
                if back_button.clicked(event):
                    state = "menu"

            elif state == "game":
                if event.type == pygame.MOUSEMOTION:
                    posx = event.pos[0]
                if restart_button.clicked(event):
                    game = Game(game.level)
                elif menu_button.clicked(event):
                    state = "levels"
                elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                      and not game.busy and not game.game_over
                      and BX <= event.pos[0] < BX + BOARD_W and event.pos[1] < BY + BOARD_H):
                    col = (event.pos[0] - BX) // SQ
                    if is_valid_location(game.board, col):
                        game.start_drop(col, PLAYER_PIECE)

        # ---- render
        screen.blit(background, (0, 0))

        if state == "menu":
            draw_text(screen, title_font, "Connect Four", WHITE, (WIDTH // 2, 200))
            for i in range(4):
                piece = PLAYER_PIECE if i % 2 == 0 else AI_PIECE
                bob = math.sin(now / 300 + i) * 6
                draw_piece(screen, piece, (WIDTH // 2 - 135 + i * 90, 320 + bob), 32)
            play_button.draw(screen, mouse)
            draw_text(screen, tiny_font, "Get four in a row before the bot does", MUTED,
                      (WIDTH // 2, 560), shadow=False)

        elif state == "levels":
            draw_text(screen, title_font, "Select Level", WHITE, (WIDTH // 2, 150))
            for b in level_buttons + [back_button]:
                b.draw(screen, mouse)

        elif state == "game":
            g = game
            g.update_anim()

            # top bar: level + whose turn
            draw_text(screen, small_font, f"Level: {g.level}", MUTED, (90, 30), shadow=False)
            draw_text(screen, small_font, f"Moves: {len(g.history)}", MUTED, (WIDTH - 80, 30), shadow=False)
            if g.game_over:
                text, color = g.message
                draw_text(screen, big_font, text, color, (WIDTH // 2, 40))
            elif g.anim:
                pass
            elif g.turn == PLAYER:
                draw_text(screen, small_font, "Your turn", RED, (WIDTH // 2, 30), shadow=False)
            else:
                dots = "." * (1 + (now // 300) % 3)
                draw_text(screen, small_font, f"Bot is thinking{dots}", YELLOW, (WIDTH // 2, 30), shadow=False)

            # previous moves line
            draw_text(screen, tiny_font, g.last_move_text(), WHITE, (WIDTH // 2, 70), shadow=False)

            # hover column highlight + preview piece
            hover_col = (posx - BX) // SQ if BX <= posx < BX + BOARD_W else None
            if hover_col is not None and not g.busy and not g.game_over and is_valid_location(g.board, hover_col):
                col_surf = pygame.Surface((SQ, BOARD_H), pygame.SRCALPHA)
                col_surf.fill((255, 255, 255, 28))
                screen.blit(col_surf, (BX + hover_col * SQ, BY))
                draw_piece(screen, PLAYER_PIECE, (BX + hover_col * SQ + SQ // 2, HOVER_Y))

            # pieces (behind the board overlay)
            for r in range(ROW_COUNT):
                for c in range(COLUMN_COUNT):
                    if g.board[r][c] != EMPTY:
                        draw_piece(screen, g.board[r][c], cell_center(r, c))
            if g.anim:
                a = g.anim
                draw_piece(screen, a["piece"], (BX + a["col"] * SQ + SQ // 2, a["y"]))

            screen.blit(board_overlay, board_pos)

            # highlight the previous step: last move for each side
            pulse = 3 + int(2 * (1 + math.sin(now / 180)))
            for row, col, piece in g.history[-2:]:
                is_latest = (row, col, piece) == g.history[-1]
                color = WHITE if is_latest else MUTED
                pygame.draw.circle(screen, color, cell_center(row, col), RADIUS + 2, pulse if is_latest else 2)
            if g.history:
                row, col, _ = g.history[-1]
                x, y = cell_center(row, col)
                draw_text(screen, tiny_font, "last", WHITE, (x, y - RADIUS - 8), shadow=True)

            # winning four
            if g.win_cells:
                for r, c in g.win_cells:
                    pygame.draw.circle(screen, GREEN, cell_center(r, c), RADIUS + 3, 6)
                (r1, c1), (r2, c2) = g.win_cells[0], g.win_cells[-1]
                pygame.draw.line(screen, GREEN, cell_center(r1, c1), cell_center(r2, c2), 8)

            # bottom bar
            for b in (restart_button, menu_button):
                b.draw(screen, mouse)

        pygame.display.flip()
        await asyncio.sleep(0)  # hand control back to the browser every frame
        clock.tick(60)

        # ---- AI move (after the "thinking" frame has been shown)
        if (state == "game" and game.turn == AI and not game.game_over and game.anim is None
                and pygame.time.get_ticks() >= game.ai_ready_time):
            col, _ = minimax(game.board, game.depth, -math.inf, math.inf, True)
            if col is not None and is_valid_location(game.board, col):
                game.start_drop(col, AI_PIECE)


asyncio.run(main())
