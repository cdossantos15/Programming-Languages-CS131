from asyncio import get_event_loop, open_connection, create_task, Protocol
from aiohttp import ClientSession
from collections import namedtuple
from os import remove
import logging, time, json, sys

API_KEY = "AIzaSyCmTtuKOzcCoevZhjxcAg5CveKwi4DCU8I"

Client = namedtuple('Client', ['location', 'time_sent', 'AT_message'])
clients = {}

Server = namedtuple('Server', ['port', 'server_connections'])
servers = {
    'Goloman':  Server(12300, []),
    'Hands':    Server(12301, []),
    'Holiday':  Server(12302, []),
    'Welsh':    Server(12303, []),
    'Wilkes':   Server(12304, [])
}



#connects the servers to each other
def connect(s, list_servers):
    for s2 in list_servers:
        servers[s].server_connections.append(servers[s2].port)
        servers[s2].server_connections.append(servers[s].port)


connect('Goloman', ['Hands', 'Holiday', 'Wilkes'])
connect('Hands', ['Wilkes'])
connect('Holiday', ['Welsh', 'Wilkes'])


#BASED ON https://docs.python.org/3/library/asyncio-protocol.html
class ServerProtocol(Protocol):

    #create the connections
    def connection_made(self, transport):
        logging.info("STARTING UP...")
        self.transport = transport

    def data_received(self, data):
        message = data.decode()
        args = message.split()
        logging.info("RECEIVED: " + message)
        # CHECK IF A VALID MESSAGE TYPE OR RETURN ERROR
        # https://docs.python.org/3/library/asyncio-task.html#id4
        if len(args) == 4 and args[0] == 'WHATSAT':
            create_task(self.send_WHATSAT(message))
        elif len(args) == 4 and args[0] == 'IAMAT':
            create_task(self.send_IAMAT(message))
        elif len(args) == 6 and args[0] == 'AT':
            create_task(self.send_AT(message))
        else:
            self.respond("? " + message)

    # CHECK IF IAMAT MESSAGE
    async def send_IAMAT(self, message):
        args = message.split()
        try:
            time_sent = float(args[3])
        except ValueError:
            self.respond("? " + message)
            return
        if not check_location(args[2]):
            self.respond("? " + message)
            return
        AT_message = "AT " + server_name + " " + skew(time_sent) + " " + " ".join(args[1:]) + "\n"
        # send AT command to this server and respond to client
        await self.send_AT(AT_message)
        self.respond(AT_message)

    # CHECK IF WHATSAT MESSAGE
    async def send_WHATSAT(self, message):
        args = message.split()
        try:
            client_id = args[1]
            radius_km = int(args[2])
            info_bound = int(args[3])
            client = clients[client_id]
        except (ValueError, KeyError):
            self.respond("? " + message)
            return
        if info_bound > 20 or radius_km > 50:
            self.respond("? " + message)
            return
        AT_message = client.AT_message
        latitude, longitude = client.location
        radius = str(1000 * radius_km)
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + latitude + "," + longitude + "&radius=" + radius + "&key=" + API_KEY
        async with ClientSession() as session:
            json_msg = await fetch(session, url)
        # process the JSON response
        json_msg['results'] = json_msg['results'][:info_bound]
        processed_json = json.dumps(json_msg, indent=3)
        # respond with AT message appended to formatted JSON response
        self.respond(AT_message + processed_json + "\n")

    # CHECK IF AT MESSAGE
    async def send_AT(self, message):
        args = message.split()
        try:
            time_sent = float(args[5])
        except ValueError:
            self.respond("? " + message)
            return
        if not check_location(args[4]):
            self.respond("? " + message)
            return
        client_id = args[3]
        location = split_location(args[4])
        # update client record if the client_id does not already exist or the time_sent is newer
        #then, flood the information to neighboring servers
        if client_id not in clients.keys() or clients[client_id].time_sent < time_sent:
            clients[client_id] = Client(location, time_sent, message)
            for server_connections in servers[server_name].server_connections:
                await write_port(server_connections, message)


    def respond(self, message):
        logging.info("SERVER RESPONSE: " + message)
        self.transport.write(message.encode())


async def write_port(port, message):
    try:
        logging.info("Trying to connect to " + str(port) + "...")
        _, writer = await open_connection("localhost", port)
        logging.info("SUCCESSFUL connection with " + str(port) + ": " + message)
        writer.write(message.encode())
        await writer.drain()
        writer.close()
    except (ConnectionRefusedError, OSError):
        logging.info("FAILED connection with: " + str(port))


def skew(time_sent):
    time_diff = time.time() - time_sent
    if time_diff > 0:
        return "+" + str(time_diff)
    return str(time_diff)


def split_location(loc):
    args = loc.replace("+", " ").replace("-", " -").split()
    return args[0], args[1]


def check_location(loc):
    try:
        args = loc.replace("+", " ").replace("-", " ").split(" ")
        float(args[1])
        float(args[2])
        return args[0] == '' and len(args) == 3
    except (IndexError, ValueError):
        return False


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.json()


if len(sys.argv) != 2:
    print("Incorrect number of arguments: " + str(len(sys.argv)) + ". Should have 2.\n")
    exit(1)
server_name = sys.argv[1]
if server_name not in servers.keys():
    print("Invalid server name '" + server_name + "'. Must be one of: '" +
          "', '".join(servers.keys()) + "'.\n")
    exit(1)

event_loop = get_event_loop()
server_port = servers[server_name].port
coro = event_loop.create_server(ServerProtocol, "localhost", server_port)
server = event_loop.run_until_complete(coro)
log_name = server_name + "_log.txt"
try:
    remove(log_name)
except OSError:
    pass
logging.basicConfig(filename=log_name, level=logging.INFO)
try:
    event_loop.run_forever()
except KeyboardInterrupt:
    logging.info("KEYBOARD INTERRUPT")
finally:
    server.close()
    event_loop.run_until_complete(server.wait_closed())
    event_loop.close()
    logging.info("SERVER CLOSED.")