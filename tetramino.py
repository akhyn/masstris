class Piece():
    '''
    Hold basic information about a piece and manages it's rotation
    '''

    def __init__(self, piece_data):
        self.piece_data = piece_data
        self.size = len(self.piece_data['positions'][0])
        # part of the data where current shape is located
        self.shape_index = 0
        self.current_shape = self.piece_data['positions'][self.shape_index]


    def counter_clockwise(self):
        return self.piece_data['positions'][(self.size + self.shape_index -1) % self.size]


    def turn_counter_clockwise(self):
        self.shape_index = (self.size + self.shape_index -1) % self.size
        self.current_shape = self.piece_data['positions'][self.shape_index]


    def clockwise(self):
        return self.piece_data['positions'][(self.shape_index +1) % self.size]


    def turn_clockwise(self):
        self.shape_index = (self.shape_index +1) % self.size
        self.current_shape = self.piece_data['positions'][self.shape_index]

    def unsafe_shape_change(self, new_shape_index):
        self.shape_index = new_shape_index
        self.current_shape = self.piece_data['positions'][new_shape_index]

