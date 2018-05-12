# Graphics
colors = {-1: (255, 255, 255),
          0: (0, 0, 0),
          1: (255, 128, 0),
          2: (255, 128, 128),
          3: (255, 0, 128),
          4: (0, 128, 255),
          5: (128, 0, 255),
          6: (0, 255, 128),
          7: (128, 255, 0),
          8: (128, 128, 128),
          'red': (255, 0, 0),
          'black': (0, 0, 0),
          'white': (255, 255, 255),
          'blue': (0, 0, 255),
          'grey': (128, 128, 128),}
menu_anchor = (100, 100)
menu_font_ratio = 10
menu_items = ['Local Play', 'Network Play (Not enabled)', 'Quit']
units_per_col = 20
units_per_line = 15
title_min_squares_h = 27
title_min_squares_v = 9
title_text = 'Press any key'
title_tiles = [[1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1],
                        [0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0],
                        [0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1],
                        [0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
                        [0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1]]

# Network data
socket_time_out = 0.1
broadcast_delay = 1
time_to_expire = 5
incoming_buffer = 1024

# Board
FIELD_H_BOUND = 3
FIELD_V_BOUND = 0                   # For easier location validity checking
FIELD_WIDTH = 10
FIELD_HEIGHT = 20
EMPTY = 0
WALL = 9

# Game
QUEUE_LENGTH = 4
STARTING_TICK_LENGTH = 1
score_map = {1: 100,
             2: 300,
             3: 500,
             4: 800}
bad_block = 8
default_speed = 1
fast_speed = 5
lines_per_level = 10
side_moves_per_second = 10

#  Pieces
# Must be squares
pieces_data = [
              # type: 'I'
              {'color': 1,
               'positions': [[[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
                             [[0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0]],
                             [[0, 0, 0, 0], [0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0]],
                             [[0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0]]]},
              # type: 'J'
              {'color': 2,
               'positions': [[[2, 0, 0, 0], [2, 2, 2, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                             [[0, 2, 2, 0], [0, 2, 0, 0], [0, 2, 0, 0], [0, 0, 0, 0]],
                             [[0, 0, 0, 0], [2, 2, 2, 0], [0, 0, 2, 0], [0, 0, 0, 0]],
                             [[0, 2, 0, 0], [0, 2, 0, 0], [2, 2, 0, 0], [0, 0, 0, 0]]]},
              # type: 'L'
              {'color': 3,
               'positions': [[[0, 0, 3, 0], [3, 3, 3, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                             [[0, 3, 0, 0], [0, 3, 0, 0], [0, 3, 3, 0], [0, 0, 0, 0]],
                             [[0, 0, 0, 0], [3, 3, 3, 0], [3, 0, 0, 0], [0, 0, 0, 0]],
                             [[3, 3, 0, 0], [0, 3, 0, 0], [0, 3, 0, 0], [0, 0, 0, 0]]]},
              # type: 'O'
              {'color': 4,
               'positions': [[[0, 4, 4, 0], [0, 4, 4, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                             [[0, 4, 4, 0], [0, 4, 4, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                             [[0, 4, 4, 0], [0, 4, 4, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                             [[0, 4, 4, 0], [0, 4, 4, 0], [0, 0, 0, 0], [0, 0, 0, 0]]]},
              # type: 'S'
              {'color': 5,
               'positions': [[[0, 5, 5, 0], [5, 5, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                             [[0, 5, 0, 0], [0, 5, 5, 0], [0, 0, 5, 0], [0, 0, 0, 0]],
                             [[0, 0, 0, 0], [0, 5, 5, 0], [5, 5, 0, 0], [0, 0, 0, 0]],
                             [[5, 0, 0, 0], [5, 5, 0, 0], [0, 5, 0, 0], [0, 0, 0, 0]]]},
              # type: 'T'
              {'color': 6,
               'positions': [[[0, 6, 0, 0], [6, 6, 6, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                             [[0, 6, 0, 0], [0, 6, 6, 0], [0, 6, 0, 0], [0, 0, 0, 0]],
                             [[0, 0, 0, 0], [6, 6, 6, 0], [0, 6, 0, 0], [0, 0, 0, 0]],
                             [[0, 6, 0, 0], [6, 6, 0, 0], [0, 6, 0, 0], [0, 0, 0, 0]]]},
              # type: 'Z'
              {'color': 7,
               'positions': [[[7, 7, 0, 0], [0, 7, 7, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                             [[0, 0, 7, 0], [0, 7, 7, 0], [0, 7, 0, 0], [0, 0, 0, 0]],
                             [[0, 0, 0, 0], [7, 7, 0, 0], [0, 7, 7, 0], [0, 0, 0, 0]],
                             [[0, 7, 0, 0], [7, 7, 0, 0], [7, 0, 0, 0], [0, 0, 0, 0]]]}]