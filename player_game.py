import time
import random

from collections import deque

import display_game
import piece_generator


class ActiveBoard(display_game.Board):
    """Represent a classic Tetris Board"""
    from data import QUEUE_LENGTH, STARTING_TICK_LENGTH, score_map, bad_block,\
        default_speed, fast_speed, lines_per_level, EMPTY

    def __init__(self, ghost):
        """"""
        super().__init__(ghost)

        # Set where new pieces spawn
        self.SPAWN_ROW = 0
        self.SPAWN_COL = len(self.NEW_LINE)//2 - 2        # Larger than any piece's gap to its side

        # Piece generator
        self.pieces = deque()
        self.piece_gen = piece_generator.PieceGen()

        # Get first piece started
        self.bonus_lines = False
        self.next_piece()

        # Prepare needed variables
        self.hold_lock = False
        self.hold_piece = None
        self.move_time = False
        self.lines_cleared = 0
        self.level = 1
        self.base_tick = self.STARTING_TICK_LENGTH
        self.light_speed_flag = 1

    def clear_full_lines(self):
        """Remove filled lines from the board"""
        full_lines = []

        # Check each row in turn for lack of an empty slot and add to list
        for row in reversed(range(len(self.board) - self.BOTTOM_BUFFER)):
            if self.EMPTY not in self.board[row]:
                full_lines.append(row)
        cleared_count = len(full_lines)

        # Remove the full lines and replace with empy row
        for full in reversed(full_lines):
            self.board.pop(full)
            self.board.insert(0, [item for item in self.NEW_LINE])

        # Update game data
        if cleared_count > 0:
            self.lines_cleared += cleared_count
            self.level_up()
            self.score += self.level * self.score_map[cleared_count]
            # Cleared lines counter incoming lines
            if self.bonus_lines:
                self.bonus_lines -= cleared_count
                if self.bonus_lines <= 0:
                    self.bonus_lines = False
                    cleared_count = 0
            self.report('clear' + str(cleared_count))

    def next_piece(self):
        """Perform needed operations to spawn next piece"""
        # Check if we have any bonus lines queued to be added to the field
        if self.bonus_lines:
            # Pick empty slot in bonus lines
            empty = random.randint(self.FIELD_H_BOUND, self.FIELD_H_BOUND + self.FIELD_WIDTH - 1)
            # Spawn one new line per bonus line, pushing others to the top
            for _ in range(self.bonus_lines):
                self.board.pop(0)
                row = self.FIELD_HEIGHT - 1
                self.board.insert(row, [x for x in self.NEW_LINE])
                for col in range(self.FIELD_H_BOUND, self.FIELD_H_BOUND + self.FIELD_WIDTH):
                    if col != empty:
                        self.board[row][col] = self.bad_block
            # Reset bonus line status
            self.bonus_lines = False

        # Lock piece becomes available after current piece locks
        self.hold_lock = False

        # Refill queue
        while len(self.pieces) <= self.QUEUE_LENGTH:
            self.pieces.append(self.piece_gen.__next__())

        # Move next piece from queue to current
        self.piece = self.pieces.popleft()
        # self.piece_row = self.SPAWN_ROW
        # self.piece_col = self.SPAWN_COL
        self.piece_row, self.piece_col = self.move_to_top(self.SPAWN_ROW, self.SPAWN_COL)

        # Check if spawning is possible or if board is full
        if not self.is_position_valid(self.piece_row, self.piece_col):
            self.report('queue')
            self.report('piece')
            self.report('loss')
            return
        else:
            self.report('queue')
            self.report('piece')

        # Update ghost
        if self.ghost:
            self.ghost, dummy_col = self.move_to_top(self.piece_row, self.piece_col)
            self.ghost = self.lowest_possible()

        # reset board tick timer
        self.tick(reset=True)

    def tick(self, reset=False):
        """
        Manage the timer for moving pieces down on their own

        If gameplay tick is spent, move piece down

        Can be called to reset timer on new piece entering
        """
        if reset:
            self.tick_time = time.process_time()
        else:
            # Compare time since last tick with time allowed per level (modified by player using speed button)
            if time.process_time() - self.tick_time >= self.base_tick / (self.level * self.light_speed_flag):
                if self.piece_row == self.lowest_possible():
                    self.lock_piece()
                    self.next_piece()
                else:
                    self.move_down()
                self.tick_time = time.process_time()

    def store_piece(self):
        """Manage swap between current piece and hold piece"""
        # if hold slot is open, move piece to hold and spawn next
        if self.hold_piece is None:
            self.hold_piece = self.piece
            self.next_piece()
            self.hold_lock = True
            self.report('hold')
            self.report('piece')
        else:
            # If hold slot is taken, drop hold piece and put current piece in there
            # Only if they haven't been swapped yet
            if not self.hold_lock:
                self.piece, self.hold_piece = self.hold_piece, self.piece
                self.piece_col, self.piece_row = self.SPAWN_COL, self.SPAWN_ROW
                self.hold_lock = True
                self.report('hold')
                self.report('piece')

    def speed_up(self, fast_drop=False):
        """Manage current rate of fall for piece"""
        if fast_drop:
            self.light_speed_flag = self.fast_speed
        else:
            self.light_speed_flag = self.default_speed

    def drop(self):
        """Instant drop of current piece"""
        self.lock_piece()
        self.next_piece()

    def lock_piece(self):
        """Add current piece to the board"""
        self.piece_row = self.lowest_possible()
        for row in range(self.piece.size):
            for col in range(self.piece.size):
                if self.piece.current_shape[row][col] != self.EMPTY:
                    self.board[self.piece_row + row][self.piece_col + col] = self.piece.current_shape[row][col]
        # Update board state
        self.clear_full_lines()

    def move_to_top(self, row=None, col=None, shape=None):
        if row is None:
            row = self.piece_row
        if col is None:
            col = self.piece_col
        if shape is None:
            shape = self.piece.current_shape
        while self.is_position_valid(row - 1, col, shape):
            row -= 1
        return row, col

    def lowest_possible(self, row=None, col=None, shape=None):
        """
        Return lowest row current piece can fit

        Check each row below piece in turn
        """
        if row is None:
            row = self.piece_row
        if col is None:
            col = self.piece_col
        if shape is None:
            shape = self.piece.current_shape
        lowest_row = 0
        for test_row in range(row, len(self.board)):
            # If lower row not valid then lowest is current
            if not self.is_position_valid(test_row, col, shape):
                return lowest_row
            lowest_row = test_row
        return lowest_row

    def is_position_valid(self, test_row, test_col, shape=None):
        """
        Fast checking of potential location for a given piece
        """
        if shape is None:
            shape = self.piece.current_shape
        for row in range(len(shape)):
            for col in range(len(shape)):
                # Empty slots are marked by 0, any number means collision
                if self.board[test_row+row][test_col+col] and shape[row][col]:
                    return False
        return True

    def check_kick(self, shape):
        """
        Check whether piece rotation requires lateral movement to perform

        Return lateral movement required, or None if it exceeds the limits
        """
        # Check from smallest amount of movement to largest
        for step in range(self.piece.size):
            # Try one direction
            if self.is_position_valid(self.piece_row, self.piece_col + step, shape):
                return step
            # Then the other
            elif self.is_position_valid(self.piece_row, self.piece_col - step, shape):
                return -step
        return None

    def turn_counter_clockwise(self):
        """
        Check whether rotation is possible

        Update data if it is

        Pieces don't rotate, then convert to a different shape
        """
        # Check simple rotation first
        if self.is_position_valid(self.piece_row, self.piece_col, self.piece.counter_clockwise()):
            self.piece.current_shape = self.piece.counter_clockwise()
            self.piece.turn_counter_clockwise()
            self.report('shape')
            if self.ghost:
                self.ghost = self.lowest_possible()
        else:
            # Check if it is possible with a kick
            kick = self.check_kick(self.piece.counter_clockwise())
            if kick:
                self.piece.turn_counter_clockwise()
                self.piece_col += kick
                self.report('move')
                self.report('shape')
                if self.ghost:
                    self.ghost = self.lowest_possible()

    def turn_clockwise(self):
        """
        Check whether rotation is possible

        Update data if it is

        Pieces don't rotate, then convert to a different shape

        """
        # Check simple rotation first
        if self.is_position_valid(self.piece_row, self.piece_col, self.piece.clockwise()):
            self.piece.current_shape = self.piece.clockwise()
            self.piece.turn_clockwise()
            self.report('shape')
            if self.ghost:
                self.ghost = self.lowest_possible()
        else:
            # Check if it is possible with a kick
            kick = self.check_kick(self.piece.counter_clockwise())
            if kick:
                self.piece.turn_clockwise()
                self.piece_col += kick
                self.report('move')
                self.report('shape')
                if self.ghost:
                    self.ghost = self.lowest_possible()

    def move_left(self):
        """Move piece to the left if possible"""
        if self.is_position_valid(self.piece_row, self.piece_col - 1):
            self.piece_col -= 1
            self.report('move')
            if self.ghost:
                self.ghost = self.lowest_possible()

    def move_right(self):
        """Move piece to the right if possible"""
        if self.is_position_valid(self.piece_row, self.piece_col + 1):
            self.piece_col += 1
            self.report('move')
            if self.ghost:
                self.ghost = self.lowest_possible()

    def move_down(self):
        """Move piece down one row"""
        if self.is_position_valid(self.piece_row + 1, self.piece_col):
            self.piece_row += 1
            self.report('move')

    def unsafe_move_to(self, shape, row, col):
        """
        Used by AI routines

        No move validity checking
        """
        self.piece.unsafe_shape_change(shape)
        self.piece_row = max(row, 0)  # Prevent vertical tetramino from being too high before drop
        self.piece_col = col
        self.report('move')
        self.report('shape')

    def level_up(self):
        """Update player level"""
        self.level = 1 + self.lines_cleared // self.lines_per_level

    def report(self, info):
        """Report all gameplay status changes for handling"""
        if info == 'loss':
            self.reports.append(('loss', ()))
        elif info == 'move':
            self.reports.append(('move', self.piece_row, self.piece_col))
        elif info == 'hold':
            self.reports.append(('hold', self.hold_piece.current_shape))
        elif info == 'shape':
            self.reports.append(('shape', self.piece.current_shape))
        elif info == 'piece':
            self.reports.append(('piece', self.piece.current_shape, self.piece_row, self.piece_col))
            self.reports.append(('board', self.board))
        elif info == 'queue':
            self.reports.append(('queue', [piece.current_shape for piece in self.pieces]))
        elif 'clear' in info:
            # In the case of cleared lines, the message does double duty and also carries cleared lines count
            self.reports.append(('clear', int(info[-1:]), self.score))
        else:
            pass
