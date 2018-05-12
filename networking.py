import socket
import struct
import pickle
import time
from collections import deque


class Network:
    """
    Network interface for tetramino game
    """
    from data import socket_time_out, broadcast_delay, time_to_expire, incoming_buffer

    def __init__(self, port, multicast_address, time_to_live):
        self.port = port
        self.multicast_address = multicast_address
        self.multicast_group = (multicast_address, port)
        self.time_to_live = time_to_live

        self.set_up_sockets()
        self.reset_data()

    def loop(self):
        """
        Control structure of the network thread

        Controlled by the main thread through task variable
        """
        while True:
            if self.task == 'reset':
                # Start up or after a game
                self.reset_data()
            elif self.task == 'sync':
                # Client for multi host game
                self.sync()
            elif self.task == 'sync_master':
                # Master host for multi host game
                self.sync_master()
            elif self.task == 'game':
                # Game in progress - both master and client
                self.game()
            else:
                # Fallback on scanning local network for other hosts
                self.task = 'scan'
                self.scan_local_network()

    def set_up_sockets(self):
        '''
        Prepare local network sockets for datagram exchange

        Incoming socket should have short timeout for loops to function smoothly and
        buffer large enough to handle board data

        Outgoing socket is a multicast socket
        '''
        # Set up outgoing socket
        self.sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Time-to-live encoded as signed byte
        ttl = struct.pack('b', self.time_to_live)
        self.sock_out.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

        # Set up incoming socket
        self.sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_in.settimeout(self.socket_time_out)
        # Bind to all network interfaces
        server_address = ('', self.port)
        self.sock_in.bind(server_address)
        # Set up multicast group on all interfaces.
        group = socket.inet_aton(self.multicast_address)
        multi = struct.pack('4sL', group, socket.INADDR_ANY)
        self.sock_in.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, multi)

    def reset_data(self):
        '''
        Prepares all variables for a fresh scan

        Called upon startup and after each game
        '''
        self.sync_status = {}
        self.task = 'scan'
        self.game_data = None
        self.my_data = None
        self.messages = deque()
        self.game_updates = deque()
        self.host_data = {}

        # Find local network IP address
        try:
            self.sock_out.connect(('10.255.255.255', 1))
            self.my_IP = self.sock_out.getsockname()[0]
        except:
            self.my_IP = '127.0.0.1'
        self.host_name = socket.gethostname()
        self.host_data[self.my_IP] = {'status': None,
                                      'host': None,
                                      'players': None,
                                      'max': None,
                                      'AI': None}

    def scan_local_network(self):
        """
        Listen to local network for other games

        Update host data when recieved
        """
        my_task = 'scan'
        last_msg = time.process_time()

        # Exit if main program requests, otherwise keep listening
        while self.task == my_task:
            if time.process_time() - last_msg > self.broadcast_delay and self.my_data != None:
                self.update_status()
                last_msg = time.process_time()
            try:
                # Check for messages
                payload, origin = self.sock_in.recvfrom(self.incoming_buffer)
                IP = origin[0]
                msg_task, data = pickle.loads(payload)
                # Store and time stamp the data if message is relevant
                if IP != self.my_IP and msg_task == 'announce':
                    self.host_data.get(IP, {})
                    self.host_data[IP]['update_time'] = time.process_time()
                    for item in data:
                        self.host_data[IP][item] = data[item]
            except:
                pass

            # Check for expired host data or offline games
            current_time = time.process_time()
            pop_games = []
            for IP in self.host_data:
                if IP != self.my_IP:
                    # remove if stale or has started offline game
                    if current_time - self.host_data[IP]['update_time'] > self.time_to_expire or self.host_data[IP]['status'] == 'off':
                        pop_games.append(IP)
            # Remove unavailable clients
            for host in pop_games:
                self.host_data.pop(host, None)

        # One more broadcast on loop exit to update status
        self.update_status()

    def update_status(self):
        """
        Broadcast current game availability status

        Relies on multigroup socket
        """
        if self.my_data is not None:
            for item in self.my_data:
                self.host_data[self.my_IP][item] = self.my_data[item]
            message = pickle.dumps(('announce', self.my_data))
            self.sock_out.sendto(message, self.multicast_group)

    def sync(self):
        """
        Sync up with remote master host
        -Wait for game data from master
        -Send ack
        -Wait for sync signal

        Relies on multigroup socket
        """
        my_task = 'sync'

        # Keep track of progress, checked by main thread
        self.sync_status = {'game_data_recv': False,
                            'ack': False,
                            'sync_recv': False}

        # Wait for game data
        while self.task == my_task and not self.sync_status['game_data_recv']:
            try:
                payload, origin = self.sock_in.recvfrom(self.incoming_buffer)
                msg_task, data = pickle.loads(payload)
                if msg_task == 'game_data':
                    self.game_data = data
                    if self.my_IP in self.game_data:
                        self.sync_status['game_data_recv'] = True
            except:pass

        # Send ack
        if self.task == my_task:
            self.sock_out.sendto(pickle.dumps(('ack', ())), self.multicast_group)
            self.sync_status['ack'] = True

        # waiting for go
        while self.task == my_task and not self.sync_status['sync_recv']:
            try:
                payload, origin = self.sock_in.recvfrom(self.incoming_buffer)
                task, data = pickle.loads(payload)
                if task == 'sync' and 'game_data' in payload:
                    self.sync_status['sync_recv'] = True
            except:
                pass

        # Wait for main thread to start game
        while self.task == my_task:
            time.sleep(0.1)

    def sync_master(self):
        """
        Sync up with any clients:
        -Broadcast game data for game
        -Keep track of Acks from clients
        -Send game start signal

        Relies on multigroup outgoing socket
        """
        my_task = 'sync_master'
        # Progress report checked by main thread
        self.sync_status = {'game_data_sent': False,
                            'all_acks': False,
                            'sync_sent': False}

        # Wait for main thread to release game data
        data_timeout = time.process_time()
        while self.game_data is None and time.process_time() - data_timeout < self.time_to_expire:
            if time.process_time() - data_timeout > self.time_to_expire:
                self.task = 'reset'
                return
            time.sleep(0.1)
        # Broadcast game data
        self.sock_out.sendto(pickle.dumps(('game_data', self.game_data)), self.multicast_group)
        self.sync_status['game_data_sent'] = True

        # Set up list to check on clients
        all_acks = False
        ack_list = {}
        for IP in self.game_data:
            if IP != 'AI' and IP != self.my_IP:
                ack_list[IP] = False

        # Scan for acks until all received or main thread instructs otherwise
        while self.task == my_task and not all_acks:
            try:
                # Receive acks
                payload, origin = self.sock_in.recvfrom(self.incoming_buffer)
                task, data = pickle.loads(payload)
                if task == 'ack':
                    ack_list[origin[0]] = True

                # Store received acks
                all_acks = True
                for IP in ack_list:
                    if not ack_list[IP]:
                        all_acks = False
            except:
                pass
        self.sync_status['all_acks'] = True

        # Broadcast game start sync message
        if self.task == my_task:
            self.sock_out.sendto(pickle.dumps(('sync', ())), self.multicast_group)
            self.sync_status['sync_sent'] = True

        # Wait for main thread to start game
        while self.task == my_task:
            time.sleep(0.1)

    def game(self):
        my_task = 'game'
        self.game_updates.clear()
        while self.task == my_task:
            try:
                payload, origin = self.sock_in.recvfrom(self.incoming_buffer)
                IP = origin[0]
                msg_task, data = pickle.loads(payload)
                if IP != self.my_IP and msg_task == 'game_update':
                    self.game_updates.append(data)
            except:
                pass

    def send_update(self, game_ID, report):
        payload = ('game_update', (game_ID, report))
        self.sock_out.sendto(pickle.dumps(payload), self.multicast_group)
