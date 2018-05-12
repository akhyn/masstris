from collections import deque


class Board:
    """
    Contain all the display information about a game board
    """
    from data import FIELD_H_BOUND, FIELD_V_BOUND, FIELD_WIDTH, FIELD_HEIGHT, EMPTY, WALL
    NEW_LINE = [WALL]*FIELD_H_BOUND + [EMPTY] * FIELD_WIDTH + [WALL] * FIELD_H_BOUND

    def __init__(self, ghost=False):
        # Create Board structure
        self.board = []
        for _ in range(self.FIELD_HEIGHT + self.FIELD_V_BOUND):
            self.board.append([item for item in self.NEW_LINE])

        # Expand it with bottom walls for easy movement checks
        self.BOTTOM_BUFFER = self.FIELD_WIDTH // 2
        while len(self.board) < (self.FIELD_HEIGHT + self.FIELD_V_BOUND + self.BOTTOM_BUFFER):
            self.board.append([self.WALL for _ in self.NEW_LINE])

        # Needed variables
        self.reports = deque()
        self.pieces = deque()
        self.piece = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0],[0, 0, 0, 0]]
        self.hold_piece = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0],[0, 0, 0, 0]]

        self.ghost = True if ghost else False
        self.score = 0
        self.light_speed_flag = False
