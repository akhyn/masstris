from random import shuffle
from collections import deque


import tetramino


class PieceGen:
    """
    Generate semi-random series of tetraminos

    Return:
        Next instance of Piece
    """
    from data import pieces_data

    def __init__(self):
        self.base_bag = [0, 1, 2, 3, 4, 5, 6]
        self.queue = deque()

    def __iter__(self):
        return self

    def __next__(self):
        """
        Manage piece queue

        A new randomized bag of pieces is appended at the end of the queue every time it contains less than a full set
        Each iteration returns the next tetramino instance
        """
        while len(self.queue) <= len(self.pieces_data):
            shuffle(self.base_bag)
            for piece in self.base_bag:
                self.queue.append(piece)
        return tetramino.Piece(self.pieces_data[self.queue.popleft()])
