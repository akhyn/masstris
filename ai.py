from data import FIELD_H_BOUND, FIELD_HEIGHT, FIELD_WIDTH


def AI_worker(ready_queue, todo_queue):
    """
    Basic worker for multiprocessing of AI

    Listens to todo_queue for games in need of AI calculations

    Returns new piece positions through ready_queue
    """

    def quick_fill():
        """
        Calculate ideal position to drop tetramino piece

        Constraints are:
         - A clear drop path
         - Lowest row reachable weighted by covered open slots

        Relies on board, piece_range, piece_data, rows, cols from outer function

        Returns a tuple containing new shape and new column to drop from

        Function tests each rows from the bottom up, testing each piece position at each slot before moving up
        """
        def below_piece_score():
            """
            Calculate and return a scored based on what would be under a piece

            Relies on piece_len, piece_row, board and shape from outer

            From 0 (worst) to 10 (best)
            """
            holes_total = 0
            floors_total = 0
            normals_total = 0

            # Calculate for each column
            for piece_col in range(piece_len):
                holes_this_col = 0
                floors_this_col = 0
                normals_this_col = 0
                for piece_row in reversed(range(piece_len)):  # Coming up from bottom
                    slot = board[row + piece_row][col + piece_col]
                    if shape[piece_row][piece_col] == 0:  # Empty slot: increment weight from slots underneath
                        if slot == 0:
                            holes_this_col += 1
                        elif slot == 9:
                            floors_this_col += 1
                        else:
                            normals_this_col += 1
                    else:
                        # Piece was found: tally up
                        if piece_row != piece_len - 1:
                            holes_total += holes_this_col
                            floors_total += floors_this_col
                            normals_total += normals_this_col
                            break
                        # If not found, then column is ignored

            if holes_total > 1:
                return 0
            elif holes_total == 1:
                if floors_total == 0:
                    return 1
                else:
                    return 2
            else:
                if floors_total == 0:
                    return 6
                else:
                        return 10

        def is_position_valid(test_row, test_col):
            """
            Fast checking of potential location for a given piece

            Relies on board and shape from outer function

            Returns False if position isn't valid, True otherwise
            """
            for row in range(len(shape)):
                for col in range(len(shape)):
                    # Empty slots are contain 0, any number means collision
                    if board[test_row + row][test_col + col] and shape[row][col]:
                        return False
            return True

        best_found = -1
        new_col = 0
        new_shape = 0
        for row in reversed(rows):
            for shape_index in piece_range:
                shape = piece_data['positions'][shape_index]
                for col in cols:
                    if is_position_valid(row, col):
                        # Found a slot, check above for obstructions
                        clear_above = True
                        for test_row in reversed(range(0, row)):
                            if not is_position_valid(test_row, col):
                                clear_above = False
                                break
                        if clear_above:
                            # Weight this solution and check against best so far
                            score = row + below_piece_score()
                            if score > best_found:
                                best_found = score
                                new_col = col
                                new_shape = shape_index

        return new_shape, new_col

    cols = range(FIELD_H_BOUND - 1, FIELD_WIDTH + FIELD_H_BOUND - 1)
    rows = range(0, FIELD_HEIGHT)

    # Main worker loop
    item_in_queue = False
    while item_in_queue != - 1:
        item_in_queue = todo_queue.get()
        if item_in_queue and item_in_queue != - 1:
            game_ID, board, piece_data, piece_row = item_in_queue
            piece_len = len(piece_data['positions'])
            piece_range = range(piece_len)
            new_shape, new_col = quick_fill()
            ready_queue.put((game_ID, new_shape, new_col))
            item_in_queue = False
