import pygame
import threading
import multiprocessing
import time
import sys
import random
import os
import glob
from collections import deque

import graphics
import player_game
import display_game
import networking
import ai


class Screen:
    """
    Base class for game screens
    """
    def __init__(self):
        global display
        self.next = self
        self.is_connected = False

    def switch_to(self, next_screen):
        """"""
        self.next = next_screen

    def process_events(self):
        """"""
        pass

    def process_input(self):
        """"""

    def update_display(self):
        """"""
        pass

    def receive(self):
        """"""
        pass

    def send(self):
        """"""
        pass

    def process_AI(self):
        pass


class MainScreen(Screen):
    """
    Main screen for game selection
    """
    from data import menu_items

    def __init__(self):
        super().__init__()
        global network

        self.host_data = {}
        self.selection = 0
        self.next = self
        self.status_update_time = None

        # Music
        global music
        if music:
            play_next_song(menu=True)

    def process_events(self):
        """
        Update broadcast data based on current settings
        """
        global local_players_count
        global max_games
        global run_AI
        network.my_data = {'status': network.task,
                           'host': network.host_name,
                           'players': local_players_count,
                           'max': max_games,
                           'AI': run_AI}

    def process_input(self):
        """
        Process all relevant pygame events and update game state
        """
        global run_AI
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            elif event.type == pygame.KEYDOWN:
                try:
                    action = menu_keys[pygame.key.name(event.key)]
                    if action == 'quit':
                        quit_game()
                    elif action == 'move_right':
                        self.move_right()
                    elif action == 'move_left':
                        self.move_left()
                    elif action == 'move_up':
                        self.move_up()
                    elif action == 'move_down':
                        self.move_down()
                    elif action == 'validate':
                        self.validate()
                    elif action == 'ai toggle':
                        global run_AI
                        run_AI = not run_AI
                except:
                    pass

            elif event.type == pygame.JOYHATMOTION:
                if event.value[0] == -1:
                    self.move_left()
                elif event.value[0] == 1:
                    self.move_right()
                elif event.value[1] == 1:
                    self.move_up()
                elif event.value[1] == -1:
                    self.move_down()

            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    self.validate()
                if event.button == 3:
                    run_AI = not run_AI

    def update_display(self):
        """
        Call graphics routine
        """
        global run_AI
        display.main_screen(self.selection, local_players_count, run_AI)

    def move_up(self):
        if self.selection > 0:
            self.selection -= 1

    def move_down(self):
        if self.selection < len(self.menu_items) - 1:
            self.selection += 1

    def move_right(self):
        global local_players_count
        if local_players_count < max_actives:
            local_players_count += 1

    def move_left(self):
        global local_players_count
        if local_players_count > 1:
            local_players_count -= 1

    def validate(self):
        if self.selection == 2:
            quit_game()
        elif self.selection == 1:
            is_connected = True
        else:
            is_connected = False

        # force update our status before moving on
        self.process_events()

        self.next = LoadScreen(is_connected)


class LoadScreen(Screen):
    """
    Object controlling the networking aspect:

    Simple passthrough for local only, controlled by main loop for network game
    """
    from data import time_to_expire

    def __init__(self, is_connected=False):
        """
        Prepare needed variables

        Call for start of game screen if local only
        """
        super().__init__()
        global display
        global network
        self.is_connected = is_connected

        if not is_connected:
            # start solo game
            network.task = 'scan'
            game_data = self.dispatcher()
            self.next = GameScreen(game_data, is_master=True, is_connected=False)

        self.game_started = False

    def process_input(self):
        """
        Check pygame events for starting a game
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                try:
                    action = menu_keys[pygame.key.name(event.key)]
                    if action == 'quit':
                        network.task = 'reset'
                        self.next = MainScreen()
                    else:
                        network.my_data['status'] = 'start'
                except:
                    pass

    def process_events(self):
        """
        Check if a game has been initiated by a host and manage synchronization
        """
        def find_main_host():
            """
            Return key for best host for AI, dispatch and other centralized gameplay functions

            Deterministic
            """
            host_data = network.host_data
            best_pick = None
            for IP in host_data:
                # set best_pick to first element if None
                if best_pick is None:
                    best_pick = IP
                # for all the hosts that can run AI
                if host_data[IP]['AI'] is True:
                    # pick highest max
                    if host_data[IP]['max'] > host_data[best_pick]['max']:
                        best_pick = IP
                        # if equal pick max host
                        if host_data[IP]['max'] == host_data[best_pick]['max']:
                            if max(host_data[IP]['host'], host_data[best_pick]['host']) == host_data[IP]['host']:
                                best_pick = IP
            return best_pick

        def decode_game_data(encoded_data=''):
            """
            Decode remote game data and return it

            In the form:
            'host1%start_range%end_range&host2%start_range%end_range...'
            """
            decoded_data = {}
            try:
                hosts = encoded_data.split('&')
                for host in hosts:
                    items = host.split('%')
                    decoded_data[items[0]] = {'start_range': int(items[1]), 'end_range': int(items[2])}
            except (KeyError, IndexError):
                pass
            return decoded_data

        if self.game_ready():
            # check whether this host is the master
            master_IP = find_main_host()
            is_master = bool(master_IP == network.my_IP)

            if is_master:
                # set up game data
                network.game_data = self.dispatcher(True)
                # sync up other games
                network.task = 'sync_master'
                # Delay to give clients a headstart
                time.sleep(1)
            else:
                # sync with master
                network.task = 'sync'

            time_out = time.process_time()
            while time.process_time() - time_out < self.time_to_expire:
                ready = True
                for ready_item in network.sync_status:
                    if not ready_item:
                        ready = False
                if ready:
                    decoded_data = decode_game_data(network.game_data)
                    # Make certain this host is in game and join
                    if network.my_IP in decoded_data:
                        self.next = GameScreen(decoded_data, is_master, self.is_connected)
                        network.task = 'game'
                        return
                    else:
                        # Reset scan results
                        for IP in network.host_data:
                            network.host_data[IP]['status'] = ''

            # If something failed
            network.task = 'reset'
            self.next = MainScreen()

    def game_ready(self):
        """
        Check if any game on host data started a game and return True if found
        """
        for IP in network.host_data:
            if network.host_data[IP]['status'] == 'start':
                return True
        return False

    def dispatcher(self, encode=False):
        """
        Assign all hosts to a range of game IDs based on their advertised capabilities

        Encode game data if needed

        Return game data
        """
        def encode_game_data(data):
            """
            Encode game data into a string for network transmission
            Each host data separated by '&', each element within separated by '%'
            """
            encoded = ''
            for host in data:
                encoded = encoded + host + '%' + str(data[host]['start_range']) + '%' + str(data[host]['end_range']) + '&'
            # Drop final separation character
            return encoded[:-1]

        game_data = {}
        game_ID = 0

        # local only
        game_data[network.my_IP] = {}
        game_data[network.my_IP]['start_range'] = game_ID
        for _ in range(local_players_count):
            game_ID += 1
        game_data[network.my_IP]['end_range'] = game_ID - 1

        if self.is_connected:
            # multiplayer game
            for IP in network.host_data:
                if IP != network.my_IP:
                    game_data[IP] = {}
                    game_data[IP]['start_range'] = game_ID
                    global max_games
                    if network.host_data[IP]['players'] + game_ID <= max_games:
                        for _ in range(network.host_data[IP]['players']):
                            game_ID += 1
                        game_data[IP]['end_range'] = game_ID - 1
                    else:
                        break

        game_data['AI'] = {}
        game_data['AI']['start_range'] = game_ID
        if run_AI:
            # As many as allowed
            game_data['AI']['end_range'] = max_games - 1
        else:
            # None
            game_data['AI']['end_range'] = game_ID

        if encode:
            return encode_game_data(game_data)
        else:
            return game_data

    def update_display(self):
        """
        Call graphic routine
        """
        if self.is_connected:
            display.load_screen(network.host_data)


class TitleScreen(Screen):
    """
    Screen for the title scene before main menu
    """
    def __init__(self):
        super().__init__()
        display.set_up_title()

    def process_input(self):
        """
        Process all relevant inputs:

        Any button triggers next screen
        """
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self.next = MainScreen()

    def update_display(self):
        """
        Call graphics
        """
        display.title_screen()


class GameScreen(Screen):
    """
    Where the magic happens!

    Object controlling the set up and organization of a Tetris game, meant to be called from main loop
    """
    from data import side_moves_per_second

    def __init__(self, game_data=None, is_master=False, is_connected=False):
        """
        Prepare required variables

        Set up the data structures for the games

        Set up graphics for all games
        """
        super().__init__()
        global display
        global network
        self.is_connected = is_connected
        self.is_master = is_master
        self.pause_triggered = False
        self.winner = None
        self.updated_boards = deque()
        self.ready_games = {}
        self.lost_range = []

        # Something went wrong...
        if game_data is None:
            self.next = MainScreen()

        # Prep the games
        self.games, self.active_games, self.AI_games, self.remote_games = self.new_game_setup(game_data)

        # Prep the graphic engine
        global backgrounds
        if backgrounds is not None:
            background = backgrounds[0]
            random.shuffle(backgrounds)
        else:
            background = None
        display.set_up(len(self.games), self.active_range, self.remote_range, background=background)

        # Music
        global music
        if music:
            play_next_song()

    def new_game_setup(self, game_data=None):
        """
        Necessary tasks to organize a new game

        Calculate shifts so local games are always displayed from top left

        Populate the AI, remote, active and display game lists that will be iterated with newly created games
        """
        if game_data is None:
            game_data = {}

        # How much local games are shifted
        self.my_offset = game_data[network.my_IP]['start_range']

        # games actually played on local machine
        self.active_range = list(range(game_data[network.my_IP]['start_range'] - self.my_offset, game_data[network.my_IP]['end_range'] - self.my_offset + 1))

        if self.is_master:
            # remote games from end of active range to beginning of AI range
            self.remote_offset = 0
            if self.is_connected:
                self.remote_range = list(range(game_data[network.my_IP]['end_range'] + 1, game_data['AI']['start_range']))
            else:
                self.remote_range = []
            global run_AI
            if run_AI:
                self.AI_range = list(range(game_data['AI']['start_range'], game_data['AI']['end_range'] + 1))
            else:
                self.AI_range = []
        else:
            # To allow local games to always be first displayed
            self.remote_offset = game_data[network.my_IP]['end_range'] - game_data[network.my_IP]['start_range'] + 1
            # Remote = before active range, and between active range and AI
            self.remote_range = []
            for game in range(0 + self. remote_offset, game_data[network.my_IP]['end_range'] + 1):
                self.remote_range.append(game)
            for game in range(game_data[network.my_IP]['end_range'] + 1, game_data['AI']['end_range'] + 1):
                self.remote_range.append(game)

            # AI range null
            self.AI_range = []

        # Prepare the data structures
        active_games = []
        AI_games = []
        remote_games = []
        games = []
        for _ in range(len(self.active_range) + len(self.remote_range) + len(self.AI_range)):
            active_games.append(None)
            AI_games.append(None)
            remote_games.append(None)
            games.append(None)

        global ghost
        now = time.process_time()
        for index in range(len(games)):
            # Populate actively played games
            if index in self.active_range:
                new_local_game = player_game.ActiveBoard(ghost)
                new_display_game = display_game.Board(ghost)
                active_games[index] = new_local_game
                games[index] = new_display_game

            # Populate remote games
            elif index in self.remote_range and self.is_connected:
                new_display_game  = display_game.Board(ghost=False)
                remote_games[index] = new_display_game
                games[index] = new_display_game

            # Populate AI games
            elif index in self.AI_range and self.is_master and run_AI:
                new_AI_game = player_game.ActiveBoard(ghost=False)
                new_display_game = display_game.Board(ghost=False)
                AI_games[index] = new_AI_game
                games[index] = new_display_game
                # Delay first move to avoid early performance bottlenecks
                self.ready_games[index] = now + random.randint(100, 300) / 200
            else:pass

        # Network game started with no other hosts
        if self.remote_range == []:
            self.is_connected = False

        # For continuous lateral movement
        self.lateral_timers = {}

        return games, active_games, AI_games, remote_games

    def update_display(self):
        """
        Call graphic routine and clear updated boards tracker
        """
        if len(self.updated_boards) > 0:
            display.draw(self.games, self.updated_boards, self.winner)
            self.updated_boards.clear()

    def process_input(self):
        """
        Process gameplay input

        Iterate through each input event to apply appropriate gameplay action

        Keyboard: Each key is linked to a specific game
        Gamepads/Joysticks: each is linked to a specific game

        Return whether gameplay is paused
        """
        #Process all pygame events
        now = time.process_time()
        for event in pygame.event.get():
            global players_with_sound
            if event.type == pygame.QUIT:
                quit_game()
            elif event.type == SONG_END:
                play_next_song()
            # Keyboard button pressed
            elif event.type == pygame.KEYDOWN:
                try:
                    game_ID, action = game_keys[pygame.key.name(event.key)]
                    if action == 'quit':
                        self.next = MainScreen()
                    if self.active_games[game_ID] is not None:
                        if action == 'pause' and self.is_master and not self.is_connected:
                            self.pause_triggered = not self.pause_triggered
                        elif self.pause_triggered:
                            return self.pause_triggered
                        elif action == 'move right':
                            if game_ID < players_with_sound:
                                play_sound_effect('move')
                            self.lateral_timers[game_ID] = ('right', now)
                            self.active_games[game_ID].move_right()
                        elif action == 'move left':
                            if game_ID < players_with_sound:
                                play_sound_effect('move')
                            self.lateral_timers[game_ID] = ('left', now)
                            self.active_games[game_ID].move_left()
                        elif action == 'turn counter-clockwise':
                            if game_ID < players_with_sound:
                                play_sound_effect('turn')
                            self.active_games[game_ID].turn_counter_clockwise()
                        elif action == 'turn clockwise':
                            if game_ID < players_with_sound:
                                play_sound_effect('turn')
                            self.active_games[game_ID].turn_clockwise()
                        elif action == 'speed up':
                            self.active_games[game_ID].speed_up(True)
                        elif action == 'hard drop':
                            if game_ID < players_with_sound:
                                play_sound_effect('drop')
                            self.active_games[game_ID].drop()
                        elif action == 'hold':
                            if game_ID < players_with_sound:
                                play_sound_effect('store')
                            self.active_games[game_ID].store_piece()
                        elif action == 'light up':
                            self.games[game_ID].light_speed_flag = True
                            self.updated_boards.append(game_ID)
                except:
                    pass

            # Keyboard key released
            elif event.type == pygame.KEYUP:
                try:
                    game_ID, action = game_keys[pygame.key.name(event.key)]
                    if self.active_games[game_ID] != None:
                        if action == 'light up':
                            self.games[game_ID].light_speed_flag = False
                            self.updated_boards.append(game_ID)
                        elif action == 'speed up':
                            self.active_games[game_ID].speed_up(False)
                        elif action == 'move left':
                            del self.lateral_timers[game_ID]
                        elif action == 'move right':
                            del self.lateral_timers[game_ID]
                except:
                    pass

            # Gamepad Hat movement
            elif event.type == pygame.JOYHATMOTION:
                try:
                    game_ID = joysticks[event.joy]
                    if event.value[0] == -1:
                        if game_ID < players_with_sound:
                            play_sound_effect('move')
                        self.active_games[game_ID].move_left()
                        self.lateral_timers[game_ID] = ('left', now)
                    elif event.value[0] == 1:
                        if game_ID < players_with_sound:
                            play_sound_effect('move')
                        self.active_games[game_ID].move_right()
                        self.lateral_timers[game_ID] = ('right', now)
                    elif event.value[0] == 0:
                        del self.lateral_timers[game_ID]
                    elif event.value[1] == 1:  # HAT up
                        if game_ID < players_with_sound:
                            play_sound_effect('drop')
                        self.active_games[game_ID].drop()
                    elif event.value[1] == -1:  # HAT down
                        if game_ID < players_with_sound:
                            play_sound_effect('drop')
                        self.active_games[game_ID].drop()
                except:
                    pass

            # Gamepad button pressed
            elif event.type == pygame.JOYBUTTONDOWN:
                game_ID = joysticks[event.joy]
                if event.button == 0:
                    if game_ID < players_with_sound:
                        play_sound_effect('drop')
                    self.active_games[game_ID].drop()
                elif event.button == 2:
                    if game_ID < players_with_sound:
                        play_sound_effect('turn')
                    self.active_games[game_ID].turn_counter_clockwise()
                elif event.button == 1:
                    if game_ID < players_with_sound:
                        play_sound_effect('turn')
                    self.active_games[game_ID].turn_clockwise()
                elif event.button == 3:
                    if game_ID < players_with_sound:
                        play_sound_effect('store')
                    self.active_games[game_ID].store_piece()
                elif event.button == 5:
                    self.active_games[game_ID].speed_up(True)
                elif event.button == 4:
                    self.games[game_ID].light_speed_flag = True
                    self.updated_boards.append(game_ID)

            # Gamepad button released
            elif event.type == pygame.JOYBUTTONUP:
                game_ID = joysticks[event.joy]
                if event.button == 4:
                    self.games[game_ID].light_speed_flag = False
                    self.updated_boards.append(game_ID)
                elif event.button == 5:
                    self.active_games[game_ID].speed_up(False)

        # Track which games are still attempting button held down type moves and check if they are ready to act again
        for game in self.lateral_timers:
            if self.lateral_timers[game][0] == 'left' and now - self.lateral_timers[game][1] > 1 / self.side_moves_per_second:
                if game < players_with_sound:
                    play_sound_effect('move')
                self.active_games[game].move_left()
                self.lateral_timers[game] = ('left', now)
            elif self.lateral_timers[game][0] == 'right' and now - self.lateral_timers[game][1] > 1 / self.side_moves_per_second:
                if game < players_with_sound:
                    play_sound_effect('move')
                self.active_games[game].move_right()
                self.lateral_timers[game] = ('right', now)

        return self.pause_triggered

    def process_events(self):
        """
        Process all the various events of this frame:
        -All reports for each game
        -Perform end of tick maintenance
        -End if winning condition
        """
        def process_reports(reports, game_ID, broadcast):
            """
            Loop through all reports in the queue for a given game.

            Manage data as needed for each (update display, score...)

            Broadcast update if needed (remote games)

            Clear report queue on exit
            Return True if game is still ongoing, False if it lost

            """
            def encode_board(report):
                """
                Encode board data report for network transmission

                Board report in the form of (game_ID, board_data)

                Result is a string where each line is separated by ':'

                Return report as (game_ID, encoded_board)
                """
                # Create a string from each element in a row, for each row
                encoded = ''
                for row in range(len(self.games[game_ID].board)):
                    for col in range(len(self.games[game_ID].board[0])):
                        encoded = encoded + str(self.games[game_ID].board[row][col])
                    # Omit ':' for last row
                    if row != len(self.games[game_ID].board) - 1:
                        encoded = encoded + ':'

                return report[0], encoded

            # For graphic performance: track whether this game has changed this frame
            self.updated_boards.append(game_ID)

            # Loop through reports
            for report in reports:
                if report[0] == 'loss':
                    if len(self.games) > 1:
                        self.games[game_ID].score = -1
                    else:
                        self.winner = 0
                    return False
                elif report[0] == 'winner':
                    self.winner = report[1]
                elif report[0] == 'move':
                    # Update piece position
                    self.games[game_ID].piece_row = report[1]
                    self.games[game_ID].piece_col = report[2] - 3
                elif report[0] == 'hold':
                    # Update hold piece
                    self.games[game_ID].hold_piece = report[1]
                elif report[0] == 'shape':
                    # Update piece shape
                    self.games[game_ID].piece = report[1]
                elif report[0] == 'piece':
                    # Update piece and location
                    self.games[game_ID].piece = report[1]
                    self.games[game_ID].piece_row = report[2]
                    self.games[game_ID].piece_col = report[3] - 3
                elif report[0] == 'board':
                    # Update game board
                    self.games[game_ID].board = report[1]
                elif report[0] == 'queue':
                    # Update the piece queue
                    self.games[game_ID].pieces = []
                    for piece in report[1]:
                        self.games[game_ID].pieces.append(piece)
                elif report[0] == 'clear':
                    bad_lines = report[1] // 2
                    # Select and notify victim if master
                    if self.is_master and bad_lines > 0 and len(self.games) > 1:
                        victims = set().union(self.AI_range, self.remote_range, self.active_range)
                        victims.discard(game_ID)
                        victim = random.sample(victims, 1)[0]

                        if victim in self.AI_range:
                            self.AI_games[victim].bonus_lines = bad_lines
                        elif victim in self.active_range:
                            self.active_games[victim].bonus_lines = bad_lines
                        elif broadcast:
                            network.send_update(victim, ('bonus', bad_lines))
                    # Update score
                    self.games[game_ID].score = report[2]
                elif report[0] == 'bonus':
                    # Update game receiving bonus lines
                    if game_ID in self.AI_range:
                        self.AI_games.bonus_lines += report[1]
                    elif game_ID in self.active_games:
                        self.active_games.bonus_lines += report[1]

                if broadcast:
                    # pack up board data for size
                    if report[0] == 'board':
                        report = encode_board(report)
                    # Check for shifted games
                    if game_ID < self.remote_offset:
                        network.send_update(game_ID + self.my_offset, report)
                    else:
                        network.send_update(game_ID, report)

            reports.clear()
            return True

        def decode_board(report):
            """
            Decode board info from its string representation and return it

            Board reports are of the form (game_ID, encoded_board)

            Encoded boards are strings with each line separated by ':'

            Return (game_ID, decoded_board)
            """
            # Separate the lines and prep decoded with correct amount of elements
            decoded = report[1].split(':')
            for line in range(len(decoded)):
                # Decode each line/element
                new_line = list(decoded[line])
                decoded[line] = []
                for ch in new_line:
                    decoded[line].append(int(ch))

            return report[0], decoded

        def end_tick():
            """
            Perform clean up tasks at the end of a tick:
            -Remove lost games from active monitoring
            -Check for win condition
            -Check gameplay tick for all local games
            """
            if len(self.games) != 1:
                # remove lost games from activity checks
                for ID in invalids:
                    self.lost_range.append(ID)
                    self.active_games[ID] = None
                    self.remote_games[ID] = None
                    self.AI_games[ID] = None
                    if ID in self.active_range:
                        self.active_range.remove(ID)
                    if ID in self.remote_range:
                        self.remote_range.remove(ID)
                    if ID in self.AI_range:
                        self.AI_range.remove(ID)

                # winner detection
                if self.is_master and len(self.games) > 1:
                    if len(self.active_range) + len(self.remote_range) + len(self.AI_range) < 2:
                        for ID in range(len(self.games)):
                            if ID in self.active_range:
                                self.active_games[ID].reports.append(('winner', ID))
                            if ID in self.remote_range:
                                self.remote_games[ID].reports.append(('winner', ID))
                            if ID in self.AI_range:
                                self.AI_games[ID].reports.append(('winner', ID))

            # check for gameplay tick
            for game in self.active_games:
                if game is not None:
                    game.tick()
            for game in self.AI_games:
                if game is not None:
                    game.tick()

        if self.winner is None:
            # Extract reports from network queue and add them to correct game report queue
            # Consider limiting rate if performance suffers
            while self.is_connected and len(network.game_updates) > 0:
                # handle oldest message
                game_ID, report = network.game_updates.popleft()
                # check whether display has been moved to relocate local games
                if game_ID < self.my_offset:
                    game_ID = game_ID + self.remote_offset

                if report[0] == 'board':
                    report = decode_board(report)
                self.remote_games[game_ID].reports.append(report)

            #  process game reports for each type and note lost games
            invalids = []
            for game_ID in self.active_range:
                # Ghost piece management outside of game object for performance reasons
                global ghost
                if ghost:
                    self.games[game_ID].ghost = self.active_games[game_ID].ghost
                if len(self.active_games[game_ID].reports) > 0:
                    if not process_reports(self.active_games[game_ID].reports, game_ID, self.is_connected):
                        invalids.append(game_ID)
            for game_ID in self.remote_range:
                if len(self.remote_games[game_ID].reports) > 0:
                    if not process_reports(self.remote_games[game_ID].reports, game_ID, False):
                        invalids.append(game_ID)
            for game_ID in self.AI_range:
                if len(self.AI_games[game_ID].reports) > 0:
                    if not process_reports(self.AI_games[game_ID].reports, game_ID, self.is_connected):
                        invalids.append(game_ID)

            end_tick()

        else:
            # Game over, we have a winner
            time.sleep(3)
            self.next = MainScreen()
            pygame.event.clear()

    def process_AI(self):
        """
        Manage the AI games and the AI workers

        Relies on self.ready_games to track drop timer and
        AI_ready_queue to receive data from workers, and
        AI_todo_queue to send them AI data in need of calculation

        """
        now = time.process_time()

        # Process returns from AI workers and timestamp results
        while not AI_ready_queue.empty():
            game_ID, new_shape, new_col = AI_ready_queue.get()
            if game_ID not in self.lost_range:
                self.AI_games[game_ID].unsafe_move_to(new_shape, self.AI_games[game_ID].piece_row, new_col)
                self.ready_games[game_ID] = now

        # Check AI games for drop timer
        need_to_move = []
        for game_ID in self.ready_games:
            if game_ID not in self.lost_range and now - self.ready_games[game_ID] > 2:
                self.AI_games[game_ID].drop()
                need_to_move.append(game_ID)

        # Send AI workers the data for next move when ready
        for game_ID in need_to_move:
            del(self.ready_games[game_ID])
            AI_todo_queue.put((game_ID, self.AI_games[game_ID].board,
                               self.AI_games[game_ID].piece.piece_data,
                               self.AI_games[game_ID].piece_row))


def play_next_song(menu=False):
    global song_list
    if menu:
        pygame.mixer.music.load(menu_music)
    else:
        try:
            song_list = song_list[1:] + [song_list[0]]
            pygame.mixer.music.load(song_list[0])
        except IndexError:
            pass
    pygame.mixer.music.play()


def play_sound_effect(effect):
    global sound_effects
    if sound_effects[effect] is not None:
        effect = pygame.mixer.Sound(sound_effects[effect])
        effect.play()


def load_config(default=False):
    """
    Load configuration from file
    """
    def reset_config():
        """
        Overwrite current Configuration with default
        """
        try:
            from shutil import copyfile
            copyfile('default_configuration', 'configuration.txt')
            return 'configuration.txt'
        except:
            try:
                with open('default_configuration', encoding='utf-8'):
                    return 'default_configuration'
            except FileNotFoundError:
                quit_game()

    if default:
        config_file = reset_config()
    else:
        try:
            with open('configuration.txt', encoding='utf-8'):
                pass
        except FileNotFoundError:
            config_file = reset_config()
        config_file = 'configuration.txt'

    import configparser
    config = configparser.ConfigParser()
    config.read(config_file)

    # Gameplay
    global run_AI
    run_AI = config['Gameplay'].getboolean('AI')
    global max_games
    max_games = config['Gameplay'].getint('max games')
    global ghost
    ghost = config['Gameplay'].getboolean('ghost')

    # Video
    width = config['Video'].getint('resolution width')
    height = config['Video'].getint('resolution height')
    max_fps = config['Video'].getint('max fps')
    overscan = config['Video'].getfloat('overscan')
    fullscreen = config['Video'].getboolean('fullscreen')

    # Network
    port = config['Network'].getint('port')
    multicast = config['Network']['multicast address']
    time_to_live = config['Network'].getint('time to live')

    # input
    menu_keys = {}
    for action in config['Menu Input']:
        for key in config['Menu Input'][action].split(','):
            key = key.strip(' ')
            # key: action
            menu_keys[key] = action

    inputs = []
    game_keys = {}
    for keymap in config['Input Devices']:
        inputs.append(config['Input Devices'].getint(keymap) - 1) # for 0 index
        for action in config[keymap]:
            for key in config[keymap][action].split(','):
                key = key.strip(' ')
                # key: (player, action)
                # player converted to 0 index.get()
                game_keys[key] = ((config['Input Devices'].getint(keymap) - 1), action)

    menu_buttons = {}
    for action in config['Menu Controller']:
        for button in config['Menu Controller'][action].split(','):
            button = button.strip(' ')
            menu_buttons[button] = action

    game_buttons = {}
    for action in config['Game Controller']:
        for button in config['Game Controller'][action].split(','):
            button = button.strip(' ')
            menu_buttons[button] = action

    # Init all joysticks available and map them to games without keyboard input
    global joysticks
    joysticks = {}
    for index in range(pygame.joystick.get_count()):
        mapped_to = index
        while mapped_to in inputs:
            mapped_to += 1
        joysticks[index] = mapped_to
        inputs.append(mapped_to)
        pygame.joystick.Joystick(index).init()

    # limit active games to amount of inputs available
    global max_actives
    max_actives = max_games
    if len(inputs) < max_games:
        max_actives = len(inputs)

    global music
    music = config['Sound'].getboolean('music')
    global players_with_sound
    players_with_sound = config['Sound'].getint('max players with sound effects')

    return (width, height, fullscreen, max_fps, overscan),\
           (port, multicast, time_to_live),\
           (menu_keys, game_keys, menu_buttons, game_buttons)


def set_up():
    """
    Call up configuration loader

    Set up required variables

    Start up network thread
    """
    video_conf, network_conf, input_conf = load_config()

    # Pygame graphics
    global display
    display = graphics.Graphics(*video_conf)
    global local_players_count
    local_players_count = 1
    global backgrounds
    base_dir = os.getcwd()
    try:
        os.chdir(os.path.join(base_dir, 'data', 'backgrounds'))
        backgrounds = [os.path.join(os.getcwd(), file) for file in glob.glob('*')]
        random.shuffle(backgrounds)
    except FileNotFoundError:
        backgrounds = None
    finally:
        os.chdir(base_dir)

    # Network configuration and threads
    global network
    network = networking.Network(*network_conf)
    global net_thread
    net_thread = threading.Thread(target=network.loop)
    net_thread.daemon = True
    net_thread.start()

    # AI processes
    global AI_ready_queue
    global AI_todo_queue
    CPU_count = 1
    try:
        CPU_count = max(multiprocessing.cpu_count(), CPU_count)
    except:
        pass
    AI_ready_queue = multiprocessing.SimpleQueue()
    AI_todo_queue = multiprocessing.SimpleQueue()
    for _ in range(CPU_count):
        process = multiprocessing.Process(target=ai.AI_worker, args=(AI_ready_queue, AI_todo_queue))
        process.daemon = True
        process.start()

    # Controls
    global menu_keys
    global game_keys
    global menu_buttons
    global game_buttons
    menu_keys, game_keys, menu_buttons, game_buttons = input_conf

    # Sound
    base_dir = os.getcwd()
    global music
    global song_list
    global menu_music
    song_list = []
    if music:
        try:
            os.chdir(os.path.join(base_dir, 'data', 'music'))
            song_list = [os.path.join(os.getcwd(), file) for file in glob.glob('*.ogg') if file != 'menu.ogg']
            menu_music = os.path.join(os.getcwd(), 'menu.ogg')
            random.shuffle(song_list)
        except FileNotFoundError:
            music = False
        finally:
            os.chdir(base_dir)
    global sound_effects
    sound_effects = {
        'drop': None,
        'turn': None,
        'move': None,
        'punish': None,
        'store': None,
    }
    try:
        os.chdir(os.path.join(base_dir, 'data', 'sounds'))
        for effect in sound_effects:
            try:
                sound_effects[effect] = os.path.join(os.getcwd(), f'{effect}.wav')
            except KeyError:
                continue
    except FileNotFoundError:
        pass
    finally:
        os.chdir(base_dir)


def quit_game():
    """
    Clean up function to cleanly exit game

    Ends pygame and AI processes
    """
    global exit_triggered
    exit_triggered = True

    # Send kill signal to all AI workers
    try:
        for _ in range(max(multiprocessing.cpu_count(), 1)):
            AI_todo_queue.put(- 1)
    except:
        pass


def main():
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.mixer.init()
    pygame.init()
    # register custom event
    global SONG_END
    SONG_END = pygame.USEREVENT + 1
    pygame.mixer.music.set_endevent(SONG_END)
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.JOYBUTTONUP, pygame.JOYBUTTONDOWN, pygame.JOYHATMOTION, SONG_END])
    set_up()
    active_screen = TitleScreen()
    pause_triggered = False
    global exit_triggered
    exit_triggered = False

    # main loop
    while True:
        pause_triggered = active_screen.process_input()
        if not pause_triggered and not exit_triggered:
            active_screen.process_events()
            active_screen.process_AI()
            active_screen = active_screen.next
            active_screen.update_display()
        else:
            if exit_triggered:
                pygame.quit()
                sys.exit()
            time.sleep(0.1)


if __name__ == '__main__':
    """GLHF"""
    main()


