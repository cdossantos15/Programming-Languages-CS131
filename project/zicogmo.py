import asyncio
import aiohttp
import sys
import json
import time

API_KEY = 'AIzaSyCmTtuKOzcCoevZhjxcAg5CveKwi4DCU8I'

communications = {
	'Goloman': ['Hands', 'Holiday', 'Wilkes'],
	'Hands': ['Goloman', 'Wilkes'],
	'Holiday': ['Goloman', 'Welsh', 'Wilkes'],
	'Welsh': ['Holiday'],
	'Wilkes': ['Goloman', 'Hands', 'Holiday']
}

port_dict = {
	'Goloman': 12300,
	'Hands': 12301,
	'Holiday': 12302,
	'Welsh': 12303,
	'Wilkes': 12304
}

# Should probably be a dict of dicts, like JSON, but it's not
# Dict of client name to client information
clients = {}

def process_input(input):
	"""
	Removes leading and trailing white space from the input string, then returns an array 
	of white-space separated entries in the string
	Parameters
	--------------
		input: String containing message to process
	Returns
	--------------
		msg_arr: List of white-space separated entries in the string
	"""
	return input.strip().split()

def valid_input(msg):
	"""
	Determines if the input message array is a valid message
	IAMAT messages have exactly four entries, formatted as follows:
		IAMAT client location time_sent
	The location is checked to see if it is a valid lat/long pair
	WHATSAT messages have exactly four entries, formatted as follows:
		WHATSAT client radius num_entries
	The radius is checked to see if it is between 1 and 50 (inclusive)
	The number of entries ie checked to see if it is between 1 and 20 (inclusive)
	CHANGELOC messages have exactly seven entries, formatted as follows:
		CHANGELOC client new_loc time_sent time_received server_received
	All CHANGELOC entries of length exactly 6 are assumed to be valid,
		as they should only be sent from server to server
	All other message are not valid
	Assumes all data types are of the correct type, i.e. all castable
	Parameters
	--------------
		msg: List of important entries of the message, with all entries strings
	Returns
	--------------
		msg_type: Integer describing type of message
				1 if message is a valid "IAMAT" message
				2 if message is a valid "WHATSAT" message
				3 if message is a valid "CHANGELOC" message
				-1 if message is not valid
	"""
	if len(msg) < 1:
		return -1
	if msg[0] == "IAMAT":
		if len(msg) == 4:
			if get_lat_long(msg[2]) is not None:
				time = None
				try:
					time = float(msg[3])
				except:
					pass
				if time is None:
					return -1
				return 1
			else:
				return -1
		else:
			return -1
	elif msg[0] == "WHATSAT":
		if len(msg) == 4:
			rad = None
			try:
				rad = float(msg[2])
			except:
				pass
			if rad is None:
				return -1
			elif rad > 50 or rad <= 0:
				return -1
			else:
				num_entries = None
				try:
					num_entries = int(msg[3])
				except:
					pass
				if num_entries is None:
					return -1
				elif num_entries > 20 or num_entries <= 0:
					return -1
				else:
					return 2
		else: 
			return -1
	elif msg[0] == "CHANGELOC":
		if len(msg) == 6:
			return 3
		else:
			return -1
	else:
		return -1

def get_lat_long(input):
	"""
	Scans the input string for a latitude-longitude pair
	A valid latitude-longitude pair has exactly two +/-'s,
		serving as delimiters
	The first character must be a +/-
	The last character may not be a +/-
	
	Parameters
	--------------
		input: String containing the latitude-longitude pair
	
	Returns
	--------------
		lat_long: Tuple with first entry latitude, second entry longitude, or 
			None if the input string is not a valid pair
	"""
	# scan the input string for all instances of +/-
	instances = []
	for i in range(len(input)):
		if input[i] == '+' or input[i] == '-':
			instances.append(i)
	# More than two +/-
	if len(instances) != 2:
		return None
	# First character not a +/-
	if instances[0] != 0:
		return None
	# Last character is a +/-
	if instances[1] == len(input) - 1:
		return None
	lat_long = None
	try: 
		lat_long = float(input[:instances[1]]), float(input[instances[1]:])
	except:
		pass
	return lat_long

def process_iamat(msg_arr, time_received):
	"""
	Processes the input message array and combines it with time_received
		to create a properly-formatted array for storage
	IAMAT messages have the form
		IAMAT client location time_sent
	Parameters
	--------------
		msg_arr: List containing input IAMAT message
			msg_arr[0] - 'IAMAT'
			msg_arr[1] - client_name
			msg_arr[2] - location pair
			msg_arr[3] - time client sent
		time_received: Float containing UNIX time of when server received message
	Returns
	--------------
		client_info: List containing formatted information for storage
			client_info[0] - 'IAMAT'
			client_info[1] - client_name
			client_info[2] - location pair
			client_info[3] - time client sent
			client_info[4] - time server received
			client_info[5] - server that received the message 
	"""
	if get_lat_long(msg_arr[2]) is None:
		return None
	return [msg_arr[0], msg_arr[1], msg_arr[2], msg_arr[3], str(time_received), sys.argv[1]]

def print_client_locations():
	"""
	Prints out all client information in the dictionary
	"""
	for c,loc in list(clients.items()):
		print("Client {0} at {1}".format(c, loc))


async def flood_fill(msg, server_name):
	"""
	Asynchronously sends CHANGELOC messages to all servers this server communicates with
	Parameters
	--------------
		msg: String, the message to send
		server_name: String, the name of this server
	"""
	for s in communications[server_name]:
		log_file.write("Attempting to open connection with server {0} at port {1}...".format(s, port_dict[s]))
		try:
			reader, writer = await asyncio.open_connection('127.0.0.1', port_dict[s], loop=loop)
			log_file.write("Success\n")
			writer.write(msg.encode())
			await writer.drain()
			writer.close()
		except:
			# Could not connect
			log_file.write("Fail\n")
			pass

# This doesn't technically have to be asynchronous
async def generate_output(in_msg, time_received):
	"""
	Asynchronously creates output string for the input message, i.e. what to send to the client
	Parameters
	--------------
		in_msg: String, the raw message the client sent
		time_received: Float, the time that the server received the message
	Returns
	--------------
		out_msg: String, the raw message to send back to the client
	"""
	# Get the message in array form
	message = process_input(in_msg)
	out_msg = ""
	error_msg = "? {0}".format(in_msg)
	message_type = valid_input(message)
	# IAMAT
	if message_type == 1:
		# Update the client dictionary with new location
		msg_info = process_iamat(message, time_received)
		if msg_info is not None:
			# Store location, reported client time, time received by server
			clients[message[1]] = msg_info
			time_diff = time_received - float(message[3])
			if time_diff > 0:
				time_diff = "+" + str(time_diff)
			out_msg = ("AT {0} {1} {2}\n".format(sys.argv[1], time_diff, ' '.join(message[1:])))
			# Send CHANGELOC messages to all connected servers
			asyncio.ensure_future(flood_fill('CHANGELOC {0}\n'.format(' '.join(msg_info[1:])), sys.argv[1]))
		else:
			out_msg = error_msg
	# WHATSAT
	elif message_type == 2:
		if message[1] not in clients:
			out_msg = error_msg
		else:
			client = clients[message[1]]
			loc = get_lat_long(client[2])
			loc = str(loc[0]) + "," + str(loc[1])
			rad = float(message[2]) * 1000
			url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={0}&location={1}&radius={2}'.format(API_KEY, loc, rad)

			time_diff = float(client[4]) - float(client[3])
			if time_diff > 0:
				time_diff = "+" + str(time_diff)
			out_msg = "AT {0} {1} {2} {3} {4}\n".format(client[5], time_diff, client[1], client[2], client[3])

			async with aiohttp.ClientSession() as session:
				async with session.get(url) as resp:
					response = await resp.json()
					response['results'] = response['results'][:int(message[3])]
					out_msg += json.dumps(response, indent=3)
					out_msg += "\n\n"
	else:
		out_msg = error_msg
	return out_msg


async def handle_input(reader, writer):
	"""
	Asynchronous method that is called in a loop until a KeyboardInterrupt
	Reads the input from the reader, writes corresponding output to the writer
	Adapted from asyncio.readthedocs.io/en/latest/tcp_echo.html
	Parameters
	--------------
		reader: StreamReader instance 
		writer: StreamWriter instance
	"""
	# Read the buffer data
	data = await reader.readline()
	time_received = time.time()
	in_msg = data.decode()
	# The data already ends in a newline
	log_file.write("RECEIVED: " + in_msg)

	# Format the message to be in list form
	message = process_input(in_msg)
	# The CHANGELOC case is handled independently since there is no output to the client/other servers when received
	if message[0] == "CHANGELOC" and valid_input(message):
		# Check if the time in the message was sent later than the time currently in the dict
		if message[1] not in clients:
			clients[message[1]] = message
			asyncio.ensure_future(flood_fill('CHANGELOC {0}\n'.format(' '.join(message[1:])), sys.argv[1]))
		else:
			# This location came after the one currently stored in the dictionary
			# Don't floodfill if this is the second time you've received the message
			if message[3] > clients[message[1]][3]:
				clients[message[1]] = message
				asyncio.ensure_future(flood_fill('CHANGELOC {0}\n'.format(' '.join(message[1:])), sys.argv[1]))
	else:
		out_msg = await generate_output(in_msg, time_received)
		log_file.write("SENDING: " + out_msg)
		writer.write(out_msg.encode())
		await writer.drain()

######################################################################
# MAIN 
######################################################################

def main():
	"""
	Main function
	Parses command-line arguments to make sure they are valid
	Opens a log file for this specific server
	Runs the handle_input function asynchronously in a loop
	Adapted from asyncio.readthedocs.io/en/latest/tcp_echo.html
	"""
	if len(sys.argv) != 2:
		print("Bad args")
		sys.exit(1)
	if sys.argv[1] not in port_dict:
		print("Bad server name")
		sys.exit(1)

	global log_file
	log_file = open(sys.argv[1] + "_log.txt", "w+")

	global loop
	loop = asyncio.get_event_loop()
	coro = asyncio.start_server(handle_input, '127.0.0.1', port_dict[sys.argv[1]], loop=loop)
	server = loop.run_until_complete(coro)
	# print("Initializing server {0} at port {1}".format(sys.argv[1], port_dict[sys.argv[1]]))

	try:
		loop.run_forever()
	except KeyboardInterrupt:
		pass

	server.close()
	loop.run_until_complete(server.wait_closed())
	loop.close()
	# The log won't update until the server gets ^C'ed, which is probably bad for a server log
	log_file.close()

if __name__ == '__main__':
	main()