import pygame
import time
import random


class Graphics:
    """
    Graphics for tetramino game
    """
    from data import colors, menu_font_ratio, menu_items, title_min_squares_h, title_min_squares_v,\
        title_text, title_tiles, units_per_col, units_per_line, FIELD_WIDTH

    def __init__(self, width, height, fullscreen, max_fps=30, overscan=0):
        self.screen = pygame.display.get_surface()
        self.fullscreen = fullscreen
        if fullscreen:
            display_info = pygame.display.Info()
            self.screen_width = display_info.current_w
            self.screen_height = display_info.current_h
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN | pygame.DOUBLEBUF)
        else:
            self.screen_width = width
            self.screen_height = height
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.screen.set_alpha(None)
        self.max_fps = max_fps

        # Percentages
        self.overscan_w = self.screen_width * overscan / 100
        self.overscan_h = self.screen_height * overscan / 100

        # Fonts for menu items
        menu_text_size = self.screen_height // self.menu_font_ratio
        self.menu_font = pygame.font.Font(None, menu_text_size)
        self.small_menu_font = pygame.font.Font(None, menu_text_size // 2)

        self.background = None
        self.detail = False
        self.clock = pygame.time.Clock()

    def main_screen(self, selection, local_player_count, is_AI_on):
        self.draw_title()

        # Check menu items location (2/5th of vertical space)
        menu_vertical_space = 2 * self.screen_height // 5
        menu_splits = len(self.menu_items) + 1
        menu_step = menu_vertical_space // menu_splits
        menu_start = menu_step + 3 * self.screen_height // 5

        # Draw menu items
        for menu_item in range(len(self.menu_items)):
            height = menu_start + menu_item * menu_step
            if selection == menu_item:
                color = self.colors['red']
            else:
                color = self.colors['blue']
            text = self.menu_font.render(self.menu_items[menu_item], True, color)
            self.screen.blit(text, text.get_rect(center=(self.screen_width // 2, height)))

        # Draw player count
        count = self.small_menu_font.render(' Players: ' + str(local_player_count), True, self.colors['blue'])
        self.screen.blit(count, (0, 3 * self.screen_height // 5))

        # AI status
        if is_AI_on:
            AI_text = ' AI: ON'
        else:
            AI_text = ' AI: OFF'
        AI_text = self.small_menu_font.render(AI_text, True, self.colors['blue'])
        self.screen.blit(AI_text, (0, menu_step // 2 + 3 * self.screen_height // 5))

        pygame.display.flip()
        self.clock.tick(self.max_fps)

    def load_screen(self, remote_clients=None):
        if remote_clients is None:
            remote_clients = {}

        self.screen.fill((0, 0, 0))

        if len(remote_clients) > 0:
            font = pygame.font.Font(None, 24)
            remote_offset = 0
            for IP in remote_clients:
                name = remote_clients[IP]['host']
                player_count = remote_clients[IP]['players']
                max_players = remote_clients[IP]['max']
                host_AI = remote_clients[IP]['AI']
                IP = font.render(str(IP), True, (0, 128, 0))
                name = font.render(str(name), True, (0, 128, 0))
                player_count = font.render(str(player_count), True, (0, 128, 0))
                max_players = font.render(str(max_players), True, (0, 128, 0))
                host_AI = font.render(str(host_AI), True, (0, 128, 0))
                remote_offset += 50
                self.screen.blit(IP,(20, 20 + remote_offset))
                self.screen.blit(name,(200, 20 + remote_offset))
                self.screen.blit(player_count,(500, 20 + remote_offset))
                self.screen.blit(max_players,(600, 20 + remote_offset))
                self.screen.blit(host_AI,(700, 20 + remote_offset))

        pygame.display.flip()
        self.clock.tick(self.max_fps)

    def set_up_title(self):
        # Get size of squares based on full width and 3/5th of height
        square_size = self.screen_width // self.title_min_squares_h
        if (3 * self.screen_height) // (self.title_min_squares_v * 5) < square_size:
            square_size = (3 * self.screen_height) // (self.title_min_squares_v * 5)

        # Figure out grid size
        squares_per_line = self.screen_width // square_size
        squares_per_col = (3 * self.screen_height) // (square_size * 5)

        # And start point
        h_leftovers = self.screen_width - (square_size * squares_per_line)
        h_start = h_leftovers // 2
        v_start = 0

        # Where on grid does title start
        # Not magic numbers,
        title_x = squares_per_line // 2 - 11
        title_y = squares_per_col // 2 - 3

        # Build grid
        self.tiles = []
        for y in range(squares_per_col):
            self.tiles.append([])
            for x in range(squares_per_line):
                color = random.randint(1, 7)
                self.tiles[y].append((h_start + square_size * x, v_start + square_size * y, self.colors[color]))

        # Remove title for negative space
        for row in range(len(self.title_tiles)):
            for col in range(len(self.title_tiles[0])):
                if self.title_tiles[row][col] == 1:
                    self.tiles[row + title_y][col + title_x] = None
        self.tile_size = square_size

    def draw_title(self):
        def draw_square():
            color = self.tiles[row][col][2]
            pygame.draw.rect(self.screen,
                             (color[0] // 2, color[1] // 2, color[2] // 2),
                             pygame.Rect(self.tiles[row][col][0] + 1,
                                         self.tiles[row][col][1] + 1,
                                         self.tile_size - 2,
                                         self.tile_size - 2))
            pygame.draw.rect(self.screen,
                             color,
                             pygame.Rect(self.tiles[row][col][0] + 1,
                                         self.tiles[row][col][1] + 1,
                                         self.tile_size * 5 / 6,
                                         self.tile_size * 5 / 6))
        self.screen.fill(self.colors['black'])

        # Draw negative space logo
        for row in range(len(self.tiles)):
            for col in range(len(self.tiles[0])):
                if self.tiles[row][col] is not None:
                    draw_square()

    def title_screen(self):
        self.draw_title()

        # Draw title text
        text = self.menu_font.render(self.title_text, True, self.colors['blue'])
        self.screen.blit(text, text.get_rect(center=(self.screen_width // 2, 4 * self.screen_height // 5)))

        pygame.display.flip()
        self.clock.tick(self.max_fps)

    def set_up(self, games_count, active_range, remote_range, background=None):
        self.player_count = games_count
        self.active_range = active_range
        self.remote_range = remote_range

        self.game_start_time = time.process_time()

        # max possible size: the most that can fit for standard 20 by 10 grid with queue and info on its side
        units_per_col = self.units_per_col
        units_per_line = self.units_per_line
        unit_h = self.screen_height // units_per_col
        unit_v = self.screen_width // units_per_line
        unit = unit_h if unit_h < unit_v else unit_v # Tentative unit size is smallest that can fit in height and width

        self.shrink_factor = 1.0   # number of rows needed to display all games
        lines = 1

        #  0.0 causes crash
        if self.overscan_w == 0.0:
            self.overscan_w += 0.01
        if self.overscan_h == 0.0:
            self.overscan_h += 0.01
        # check if fits at current size
        while self.player_count * (units_per_line * unit) // (lines * self.shrink_factor) + self.overscan_w * 2 > self.screen_width and lines * (units_per_col * unit) + self.overscan_h * 2 > self.screen_height:
            # if shrink factor isn't enough for another line, increase it
            if self.shrink_factor < lines + 1:
                self.shrink_factor += 0.1
            else:
                # increase by one line and reduce shrink factor
                lines += 1
                self.shrink_factor = lines - 1

        # decrease shrink factor as long as it fits
        self.shrink_factor = lines + 1
        while self.overscan_w * 2 + self.player_count * (units_per_line * unit) // (lines * self.shrink_factor) < self.screen_width and self.overscan_h * 2 + lines * (units_per_col * unit) // self.shrink_factor < self.screen_height:
            self.shrink_factor -= 0.1

        games_per_line = 1
        while self.player_count > lines * games_per_line:
            games_per_line += 1

        # tweak unit size until the fit is perfect
        side_padding = 0
        vert_padding = 0
        temp_unit = unit
        while side_padding <= 0 or vert_padding <= 0:
            self.shrink_factor += 0.1
            # final size of a unit
            temp_unit = unit // self.shrink_factor
            # padding between boards
            side_spare_space = self.screen_width - (self.overscan_w * 2 + temp_unit * units_per_line * games_per_line)
            side_padding = side_spare_space // (games_per_line + 1)
            vert_spare_space = self.screen_height - (self.overscan_h * 2 + temp_unit * units_per_col * lines)
            vert_padding = vert_spare_space // (lines + 1)

        # Square size
        self.unit = int(temp_unit)

        # Detailed squares
        self.detail_size = self.unit // 6
        self.detail = self.detail_size
        self.game_font = pygame.font.Font(None, self.unit * 2)

        # Buffer between squares
        self.piece_indent = 1 if self.unit < 30 else 2

        # map draw coordinates for each board
        self.games_map = {}
        for line in range(lines):
            for game in range(games_per_line):
                #top left corner for each game
                self.games_map[game + games_per_line * line] = (self.overscan_w + game * self.unit * units_per_line + side_padding * (game + 1), self.overscan_h + line * self.unit * units_per_col + vert_padding * (line + 1))

        # wipe screen and paint background
        self.screen.fill(self.colors['black'])
        if background is not None:
            self.background = pygame.image.load(background).convert()
            self.screen.blit(self.background, [0, 0])
        pygame.display.flip()
        self.clock.tick(self.max_fps)

    def draw(self, games, updated_boards, winner=False):
        """
        Display the current status of the game

        Only redraws games that have been updated for speed

        Each game is a fixed amount of self.units with h_offset and v_offset as its top left corner
        Hence, background is (h_offset + unit * units_per_line, v_offset + unit * units per col
        Filling calls adjust pixel counts based on that
        """
        def draw_square(row, col, color):
            """
            Draw a square based on grid position
            """
            square_size = self.unit - self.piece_indent * 2
            square_h_offset = h_offset + (col * self.unit) + self.piece_indent
            square_v_offset = v_offset + (row * self.unit) + self.piece_indent
            if self.detail:
                detail_color = (color[0]//2, color[1]//2, color[2]//2)
                pygame.draw.rect(self.screen,
                                 detail_color,
                                 pygame.Rect(square_h_offset,
                                             square_v_offset,
                                             square_size,
                                             square_size))

                pygame.draw.rect(self.screen,
                                 color,
                                 pygame.Rect(square_h_offset,
                                             square_v_offset,
                                             (square_size - self.detail),
                                             (square_size - self.detail)))

            else:
                pygame.draw.rect(self.screen,
                                 color,
                                 pygame.Rect(square_h_offset,
                                             square_v_offset,
                                             square_size,
                                             square_size))

        def draw_piece(piece, ghost=False):
            """
            Draw a tetris piece based on its relative grid position

            Position accessed from encompassing function
            """
            for col in range(piece_size):
                for row in range(piece_size):
                    # Draw every square that isn't empty
                    if piece[row][col] != 0:
                        # Set color
                        if not ghost:
                            color = self.colors[piece[row][col]]
                        else:
                            original = self.colors[piece[row][col]]
                            color = (original[0]//2, original[1]//2, original[2]//2)
                        # Draw square
                        draw_square(piece_row + row, piece_col + col, color)

        def draw_frame():
            """
            Draw the background for each game frame based on its anchor position
            """
            # Game frame
            self.screen.fill(frame_color, pygame.Rect(h_offset, v_offset, game_width, game_height))
            # Board frame
            self.screen.fill(background_frame_color, pygame.Rect(h_offset + 1, v_offset + 1, self.FIELD_WIDTH * self.unit - 2, game_height - 2))
            # Hold background
            self.screen.fill(background_color, pygame.Rect(h_offset + self.FIELD_WIDTH * self.unit,
                                                           v_offset + 1,
                                                           game_width - self.FIELD_WIDTH * self.unit - 1,
                                                           4.5 * self.unit))
            # Queue and score background
            self.screen.fill(background_color, pygame.Rect(h_offset + self.FIELD_WIDTH * self.unit,
                                                           v_offset + 2 + 4.5 * self.unit,
                                                           game_width - self.FIELD_WIDTH * self.unit - 1,
                                                           game_height - (4.5 * self.unit) - 3))

        # Each game is the board plus queue, hold piece and score displays
        game_width = self.unit * self.units_per_line
        game_height = self.unit * self.units_per_col

        if winner:
            # Blackout all but winner board
            for game in range(len(games)):
                if game != winner:
                    h_offset, v_offset = self.games_map[game]
                    self.screen.fill(self.colors['black'], pygame.Rect(h_offset, v_offset, game_width, game_height))
            pygame.display.flip()
            self.clock.tick(self.max_fps)
            return

        for game_index in updated_boards:
            # Screen location of this game board
            h_offset, v_offset = self.games_map[game_index]

            # Set frame color
            if game_index in self.active_range:
                frame_color = self.colors['blue']
            elif game_index in self.remote_range:
                frame_color = self.colors['red']
            else:
                frame_color = self.colors['white']

            # Display background based on type of game and conditions
            # Lost game
            if games[game_index].score == -1:
                background_color = self.colors['grey']
                background_frame_color = self.colors['grey']
            # Player requested highlighting
            elif games[game_index].light_speed_flag:
                background_color = self.colors['white']
                background_frame_color = self.colors['white']
            # Normal status
            else:
                background_color = self.colors['black']
                background_frame_color = self.colors['grey']
            draw_frame()

            # Draw board contents
            for col in range(0, len(games[game_index].board[0]) - 6):
                for row in range(len(games[game_index].board) - 5):
                    color = self.colors[games[game_index].board[row][col + 3]]
                    draw_square(row, col, color)

            # Draw piece
            piece_size = len(games[game_index].piece)
            piece_col = games[game_index].piece_col

            # Draw ghost piece
            if games[game_index].ghost:
                piece_row = games[game_index].ghost
                draw_piece(games[game_index].piece, ghost=True)
            piece_row = games[game_index].piece_row
            draw_piece(games[game_index].piece)

            # Hold piece
            piece_row = 1
            piece_col = 11
            # Draw frame
            draw_piece(games[game_index].hold_piece)

            # Piece queue
            piece_row = 14
            piece_col = 11
            for piece in games[game_index].pieces:
                draw_piece(piece)
                piece_row -= 3

            # Draw score
            score = self.game_font.render(str(games[game_index].score), True, self.colors['red'])
            self.screen.blit(score, (h_offset + self.unit * 11, v_offset + self.unit * 18))

        pygame.display.flip()
        self.clock.tick(self.max_fps)

