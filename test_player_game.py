import unittest
import player_game


class TestClearLines(unittest.TestCase):
    '''
    Lines on the board that do not have an empty space should be removed and a new empty line
    created in its place at the top.
    '''
    # Set up board
    test_board = player_game.ActiveBoard(False)
    test_board.piece = test_board.piece_gen.__next__()


    def test_clear_full_lines(self):
        '''
        ==> Remove all full lines and only full lines
        '''
        # Setup board:
        #     0 1 2 3 4 5 6 7 8 9
        #  0  1 1 1 1 1 1 1 1 1 1
        #  1  . 9 . . . . . . . .
        #  2  . . 9 . . . . . . .
        #  3  . . . 9 . . . . . .
        #  4  . . . . . . . . . .
        #  5  . . . . 9 . . . . .
        #  6  . . . . . 9 . . . .
        #  7  2 2 2 2 2 2 2 2 2 2
        #  8  3 3 3 3 3 3 3 3 3 3
        #  9  . . . . . . 9 . . .
        # 10  . . . . . . . . . .
        # 11  . . . . . . . . 9 .
        # 12  . . . . . . . . 9 .
        # 13  . . 9 . . . . . . .
        # 14  9 9 . 9 9 9 9 9 9 9
        # 15  . . 9 . . . . . . .
        # 16  . . . . 9 9 . . . .
        # 17  . . . . . . . . . .
        # 18  9 . . . 9 . . . . 9
        # 19  4 4 4 4 4 4 4 4 4 4
        # Setup:
        coords = [(1, 1), (2, 2), (3, 3), (5, 4), (6, 5), (9, 6), (11, 8), (12, 8), (13, 2),(14, 0), (14, 1), (14, 3), (14, 4),
                  (14, 5), (14, 6), (14, 7), (14, 8), (14, 9), (15, 2), (16, 4), (16, 5), (18, 0), (18, 4), (18, 9)]
        for x, y in coords:
            self.test_board.board[x][y + self.test_board.FIELD_H_BOUND] = 9

        for i in range(self.test_board.FIELD_WIDTH):
            self.test_board.board[0][i + self.test_board.FIELD_H_BOUND] = 1
            self.test_board.board[7][i + self.test_board.FIELD_H_BOUND] = 2
            self.test_board.board[8][i + self.test_board.FIELD_H_BOUND] = 3
            self.test_board.board[19][i + self.test_board.FIELD_H_BOUND] = 4

        # Call function
        self.test_board.clear_full_lines()

        # New board:
        #     0 1 2 3 4 5 6 7 8 9
        #  0  . . . . . . . . . .
        #  1  . . . . . . . . . .
        #  2  . . . . . . . . . .
        #  3  . . . . . . . . . .
        #  4  . 9 . . . . . . . .
        #  5  . . 9 . . . . . . .
        #  6  . . . 9 . . . . . .
        #  7  . . . . . . . . . .
        #  8  . . . . 9 . . . . .
        #  9  . . . . . 9 . . . .
        # 10  . . . . . . 9 . . .
        # 11  . . . . . . . . . .
        # 12  . . . . . . . . 9 .
        # 13  . . . . . . . . 9 .
        # 14  . . 9 . . . . . . .
        # 15  9 9 . 9 9 9 9 9 9 9
        # 16  . . 9 . . . . . . .
        # 17  . . . . 9 9 . . . .
        # 18  . . . . . . . . . .
        # 19  9 . . . 9 . . . . 9
        # Testing individual locations for proper movement
        new_coords = [(4, 1), (5, 2), (6, 3), (8, 4), (9, 5), (10, 6), (12, 8), (13, 8), (14, 2), (15, 0), (15, 1), (15, 3), (15, 4),
                      (15, 5), (15, 6), (15, 7), (15, 8), (15, 9), (16, 2), (17, 4), (17, 5), (19, 0), (19, 4), (19, 9)]
        for new_x, new_y in new_coords:
            self.assertEqual(self.test_board.board[new_x][new_y + self.test_board.FIELD_H_BOUND], 9)

        # Nothing left from removed complete rows
        for row in range(len(self.test_board.board)):
            for col in range(len(self.test_board.NEW_LINE)):
                self.assertEqual(self.test_board.board[row][col] not in [1, 2, 3, 4, 5, 6], True)


class TestValidPositions(unittest.TestCase):
    '''
    Pieces should not be able to move on walls or already occupied locations
    '''
    # Set up board
    test_board = player_game.ActiveBoard(False)
    test_board.piece = test_board.piece_gen.__next__()

    # Testing locations
    # index: 0, 1, 2, 3, 4,  ...  11, 12, 13, 14, 15
    #        *  *  *  _  _   ...   _   _   *   *   *

    left_wall = test_board.FIELD_H_BOUND - 1
    right_wall = len(test_board.NEW_LINE) - test_board.FIELD_H_BOUND
    bottom_wall = test_board.FIELD_HEIGHT + test_board.FIELD_V_BOUND
    test_piece_row = 9
    test_piece_col = len(test_board.NEW_LINE)//2
    free_row = 4

    # Inject a piece in the middle
    test_board.board[test_piece_row][test_piece_col] = 9

    # Set up test piece
    # 0 0 0 0
    # 0 1 1 0
    # 0 0 1 0
    # 0 0 0 0
    test_board.piece.current_shape = [[0, 0, 0, 0], [0, 1, 1, 0], [0, 0, 1, 0], [0, 0, 0, 0]]
    test_size = 4
    test_board.piece.size = test_size


    def test_move_left_on_wall(self):
        '''
        ==> Piece cannot move on top of wall when moving left
        '''
        # Not touching left wall is okay
        self.assertEqual(self.test_board.is_position_valid(self.free_row, self.test_piece_col), True)
        # overlap with empty slots is okay
        self.assertEqual(self.test_board.is_position_valid(self.free_row, self.left_wall), True)
        # collision is illegal
        self.assertEqual(self.test_board.is_position_valid(self.free_row, self.left_wall -1), False)


    def test_move_right_on_wall(self):
        '''
        ==> Piece cannot move on top of wall when moving right
        '''
        # Not touching right wall is okay
        self.assertEqual(self.test_board.is_position_valid(self.free_row, self.test_piece_col), True)
        # overlap with empty slots is okay
        self.assertEqual(self.test_board.is_position_valid(self.free_row, self.right_wall - self.test_size +1), True)
        # collision is illegal
        self.assertEqual(self.test_board.is_position_valid(self.free_row, self.right_wall - self.test_size +2), False)


    def test_move_down_on_wall(self):
        '''
        ==> Piece cannot move on top of wall when moving down
        '''
        # Not touching bottom wall is okay
        self.assertEqual(self.test_board.is_position_valid(self.free_row, self.test_piece_col), True)
        # overlap with empty slots is okay
        self.assertEqual(self.test_board.is_position_valid(self.bottom_wall - self.test_size +1, self.test_piece_col), True)
        # collision is illegal
        self.assertEqual(self.test_board.is_position_valid(self.bottom_wall - self.test_size +2, self.test_piece_col), False)


    def test_move_on_occupied(self):
        '''
        ==> Piece cannot move on top of occupied slot when moving left
        '''
        # Not touching any occupied slot is okay
        self.assertEqual(self.test_board.is_position_valid(self.free_row, self.test_piece_col), True)
        # piece hole on top of occupied is okay
        self.assertEqual(self.test_board.is_position_valid(self.test_piece_row, self.test_piece_col), True)
        # overlap is not legal
        self.assertEqual(self.test_board.is_position_valid(self.test_piece_row -1, self.test_piece_col -1), False)


    def test_fast_drop_on_wall(self):
        '''
        ==> Piece cannot move on top of wall when using fast drop
        '''
        self.test_board.piece_row = self.test_piece_row + self.test_size
        self.test_board.piece_col = self.test_piece_col
        self.assertEqual(self.test_board.lowest_possible(), self.bottom_wall - self.test_size +1)



    def test_fast_drop_on_piece(self):
        '''
        ==> Piece cannot move on top of occupied slot when using fast drop
        '''
        # . . . .
        # . x x .
        # . . x .
        # . . . .
        self.test_board.piece_row = 0

        # Landing on tail
        self.test_board.piece_col = self.test_piece_col - 1
        self.assertEqual(self.test_board.lowest_possible(), self.test_piece_row - self.test_size +2)
        # landing on recess
        self.test_board.piece_col = self.test_piece_col - 2
        self.assertEqual(self.test_board.lowest_possible(), self.test_piece_row - self.test_size +1)
        # Overlap with no collision
        self.test_board.piece_col = self.test_piece_col - 3
        self.assertEqual(self.test_board.lowest_possible(), self.bottom_wall - self.test_size +1)


class TestCorrectLock(unittest.TestCase):
    '''
    Locked pieces should appear in the board data correctly
    '''
    # Set up board
    test_board = player_game.ActiveBoard(False)
    test_board.piece = test_board.piece_gen.__next__()


    def test_floor_lock(self):
        '''
        ==> Entire piece should rest on floor of board
        '''
        bottom_wall = self.test_board.FIELD_HEIGHT + self.test_board.FIELD_V_BOUND

        # Set up test piece
        self.test_board.piece_col = 5
        self.test_board.piece_row = 0
        self.test_board.piece_color = 1
        # 0 0 0 0
        # 0 1 1 0
        # 0 0 1 0
        # 0 0 0 0
        self.test_board.piece.current_shape = [[0, 0, 0, 0], [0, 1, 1, 0], [0, 0, 1, 0], [0, 0, 0, 0]]
        self.test_board.piece.size = 4

        #
        # Call tested function
        self.test_board.lock_piece()

        # Board state should be:
        # 18  x x x . . . . . . . .
        # 19  x x x . . 0 0 0 0 . .
        # 20  x x x . . 0 1 1 0 . .
        # 21  x x x . . 0 0 1 0 . .
        # 22  x x x x x x x x x x x
        for i in range(self.test_board.piece.size):
            for j in range(self.test_board.piece.size):
                if (i, j) in [(1, 1), (1, 2), (2, 2)]:
                    self.assertEqual(self.test_board.board[self.test_board.piece_row + i][self.test_board.piece_col + j],
                                 self.test_board.piece.current_shape[i][j])

        # Test with another similar drop
        self.test_board.piece_row = 0
        self.test_board.lock_piece()
        # Board state should be:
        # 18  x x x . . . . . . . .
        # 18  x x x . . . 1 1 . . .
        # 19  x x x . . . . 1 . . .
        # 20  x x x . . . 1 1 . . .
        # 21  x x x . . . . 1 . . .
        # 22  x x x x x x x x x x x
        for i in range(self.test_board.piece.size):
            for j in range(self.test_board.piece.size):
                if (i, j) in [(1, 1), (1, 2), (2, 2)]:
                    self.assertEqual(self.test_board.board[self.test_board.piece_row + i][self.test_board.piece_col + j],
                                 self.test_board.piece.current_shape[i][j])
                    # Test first piece again
                    self.assertEqual(self.test_board.board[self.test_board.piece_row + i +2][self.test_board.piece_col + j],
                                 self.test_board.piece.current_shape[i][j])



if __name__ == '__main__':
    unittest.main()
