'''
Created on 27/08/2013

This is where you do your work.
Not only do you need to fill in the methods but you can also add any other classes, 
methods or functions to this file to make your system pass all of the tests.

@author: dhad933
'''

from drive import Drive
from math import floor
import pdb
import threading

class A2File(object):
	'''
	One of these gets returned from Volume open.
	'''
	
	def __init__(self, name, parent):
		'''
		Initializes an A2File object.
		Not called from the test file but you should call this from the
		Volume.open method.
		You can use as many parameters as you need.
		[name, location, directory]
		'''
		Library.check_name_no_length(name)
		self.nme = name
		self.data = b''
		self.parent = parent
		self.local = None
	
	@staticmethod
	def read_in(name, parent, block_num, size):
		filee = A2File(name, parent)
		location = Location.create_from_drive(block_num, parent.get_volume())
		filee.local = location
		filee.data = location.get_referenced_data_unstriped()[:size]
		filee.assign_location(block_num)
		return filee
	
	@staticmethod
	def	new_file(name, parent):
		filee = A2File(name, parent)
		filee.assign_location(parent.request_block())
		return filee

	def assign_location(self, block_num):
		self.local = Location(block_num, self.parent.get_volume())
		self.local.write()

	def size(self):
		'''
		Returns the size of the file in bytes.
		'''
		return len(self.data)
	
	def name(self):
		return self.nme
	
	def write(self, location, data):
		'''
		Writes data to a file at a specific byte location.
		If location is greater than the size of the file the file is extended
		to the location with spaces. 
		'''
		if location > len(self.data):
			self.data += b' ' * (location - len(self.data))
		self.data = self.data[:location] + data + self.data[location:]
		to_write = Library.prepare_data(self.data)
		while len(to_write) > self.local.num_refs():
			self.local.add_reference(self.parent.get_volume().request_block())
		Library.write(to_write, self.local.get_list(), self.parent.get_volume().get_drive())
		self.parent.write()				
	
	def read(self, location, amount):
		'''
		Reads from a file at a specific byte location.
		An exception is thrown if any of the range from
		location to (location + amount - 1) is outside the range of the file.
		Areas within the range of the file return spaces if they have not been written to.
		'''
		if location + amount -1 > len(self.data):
			raise IOError('Location and amount specified is longer than file')
		return self.data[location:location +amount]

	def to_string(self):
		data = []
		data.append(self.name())
		data.append(Library.int_to_b(self.size()))
		data.append(Library.int_to_b(self.local.get_location()))
		return b'\n'.join(data) + b'\n'

######################  VOLUME CLASS  ######################

class Volume(object):
	'''
	A volume is the disk as it appears to the file system.
	The disk structure is to be entirely stored in ASCII so that it
	can be inspected easily. It must contain:
		Volume data blocks: the number of contiguous blocks with the volume data - as a string, ends with "\n"
		Name: at least one character plus "\n" for end of name)
		Size: as a string terminated with "\n"
		Free block bitmap: drive.num_blocks() + 1 bytes ("x" indicates used, "-" indicates free, ends with "\n")
		First block of root directory (called root_index) : as a string terminated with "\n" - always the last
			block on the drive.
	'''
	def __init__(self, drive, name):
		Library.check_name(name, drive.num_bytes())
		self.nme = name
		self.drive = drive
		self._lock = threading.Lock()
		#self.files = []
		self.bmap = [b'-']*self.size()
		for i in range(self.volume_data_blocks()):
			self.check_data_block(i)
		self.check_data_block(self.root_index())
		self.root = None

	@staticmethod
	def format(drive, name):
		'''
		Creates a new volume in a disk.
		Puts the initial metadata on the disk.
		The name must be at least one byte long and not include "\n".
		Raises an IOError if after the allocation of the volume information
		there are not enough blocks to allocate the root directory and at least
		one block for a file.
		Returns the volume.
		'''
		volume = Volume(drive, name)

		if volume.volume_data_blocks() + 2 > volume.size():
			raise IOError('Not enough space for root folder and data')
		volume.write()
		volume.create_root()
		
		return volume
	
	def create_root(self):
		self.root = Directory(b'root', self.root_index(), self)
	
	def name(self):
		'''
		Returns the volumes name.
		'''
		return self.nme
	
	
	def volume_data_blocks(self):
		'''
		Returns the number of blocks at the beginning of the drive which are used to hold
		the volume information.
		'''
		data = self.part_meta_data()
		length = len(data) + 1        #Added One for '\n' char
		blocks = floor(length / Drive.BLK_SIZE)
		while (len(str(blocks)) + length)/Drive.BLK_SIZE >= blocks:
			blocks += 1
		return blocks
		
	def size(self):
		'''
		Returns the number of blocks in the underlying drive.
		'''
		return self.drive.num_blocks()
	
	def bitmap(self):
		'''
		Returns the volume block bitmap.
		'''
		result = b''.join(self.bmap)
		return result
	
	def root_index(self):
		'''
		Returns the block number of the first block of the root directory.
		Always the last block on the drive.
		'''
		return self.size() -1
	
	@staticmethod
	def mount(drive_name):
		'''
		Reconnects a drive as a volume.
		Any data on the drive is preserved.
		Returns the volume.
		'''
		drive = Drive.reconnect(drive_name)
		inputt = drive.read_block(0)
		data = inputt.splitlines()
		length = int(data[0])
		i = 1
		while i < length:
			inputt = drive.read_block(i)
			data.extend(inputt.splitlines())
			i+=1
		i = 1
		outcome = False
		
		data[len(data)-1] = data[len(data)-1].rstrip()
	
		while len(data) > (i+1):
			while len(data) > (i+1) and data[i+1].isdigit() == outcome:
				data[i] += data[i+1]
				data.pop(i+1)
			i+=1
			outcome = not outcome
		
		volume = Volume(drive, data[1])
		for i in range(len(data[3])):                #TODO Needs better fix
			if data[3][i] == 120:
				volume.bmap[i] = b'x'
		volume.import_files()

		return volume
		
	def unmount(self):
		'''
		Unmounts the volume and disconnects the drive.
		'''
		self.drive.disconnect()
		del self
	
	def open(self, filename):		  
		'''
		Opens a file for read and write operations.
		If the file does not exist it is created.
		Returns an A2File object.
		'''
		if not self.root:
			self.create_root()
		name_list = filename.strip(b'/')
		filee = self.root.get_file(name_list)
		return filee

	def part_meta_data(self):
		data = []
		data.append(self.nme)
		data.append(Library.int_to_b(self.size()))
		data.append(self.bitmap())
		data.append(Library.int_to_b(self.root_index()))
		result = b'\n'.join(data)
		return result

	def meta_data(self):
		data = []
		data.append(Library.int_to_b(self.volume_data_blocks()))
		data.append(self.part_meta_data())
		result = b'\n'.join(data)
		return result

	def check_data_block(self, pos):
		self._lock.acquire()
		try:
			if self.bmap[pos] == b'x':
				raise IOError('Block Already in use')
			self.bmap[pos] = b'x'
		finally:
			self._lock.release()
		self.write()

	def request_block(self):
		try:
			i = self.bmap.index(b'-')
		except ValueError:
			raise IOError('No more room left in volume')
		self.check_data_block(i)
		return i

	def get_drive(self):
		return self.drive

	def write(self):
		data = Library.prepare_data(self.meta_data())
		Library.write(data, range(len(data)), self.drive)

	def import_files(self):
		self.root = Directory.import_files(b'root', self.root_index(), self)

######################  DIRECTORY CLASS  ######################

class Directory(object):
	
	def __init__(self, name, pos, vol):
		pdb.set_trace()
		Library.check_name_no_length(name)        #Can be used in the future with more Directories?
		self.name = name
		self.file = []
		self.volume = vol
		self.local = Location(pos, vol)
		self.local.write()
		self.dirs = []
	
	def get_name(self):
		return self.name

	def get_file(self, name_list):
		if len(name_list) > 1:
			for dirr in self.dirs:
				if dirr.get_name() == name_list[0]:
					return dirr.get_file(name_list.pop(0))
			self.dirs.append(Directory(name_list[0], self.volume.request_block(), self.volume))
			return self.dirs[len(self.dirs)-1].get_file(name_list.pop(0))
		name = name_list[0]
		for item in self.file:
			if item.name() == name:
				return item
		filee = A2File.new_file(name, self)
		self.file.append(filee)
		self.write()
		return filee
	
	def add_file(self, filee):
		self.file.append(filee)
		self.write()	

	def size(self):
		count = 0
		for files in self.file:
			count += len(files.name)
		return count
	
	def get_volume(self):
		return self.volume

	def write(self):		   #TODO
		to_write = b''
		for files in self.file:
			to_write += files.to_string()
		data = Library.prepare_data(to_write)
		#print('Number of Blocks required: ' + str(len(data)))
		while len(data) > self.local.total_refs():
			self.local.add_reference(self.request_block())
		#print('Actual number of Blocks: ' + str(self.local.total_refs()))
		#if len(data) >= 19:
			#print(data)
			#print('\n\n')
		Library.write(data, self.local.get_list(), self.volume.get_drive())

	def request_block(self):
		i = self.volume.request_block()
		return i
	
	@staticmethod
	def import_files(name, pos, volume):
		location = Location.create_from_drive(pos, volume)
		directory = Directory(name, pos, volume)
		directory.local = location
		data = location.get_referenced_data()

		data_list = data.split(b'\n')
		if len(data_list) == 1:
			return directory
		#print(data_list)
		for i in range(0, len(data_list), 3):
			directory.file.append(A2File.read_in(data_list[i], directory, int(data_list[i+2]), int(data_list[i+1])))
		return directory

###################### LOCATION CLASS ######################

class Location(object):
	REFERENCES = 15

	def __init__(self, location, volume):
		self.local = [0] * (Location.REFERENCES + 1)
		self.volume = volume
		self.pos = location
		self.second_tier = None

	def add_reference(self, pos):
		i = self.num_refs()
		if self.num_refs() == Location.REFERENCES and self.second_tier == None:
			second_pos = self.volume.request_block()
			self.second_tier = Location(second_pos, self.volume)
			self.local[i] = second_pos
			self.write()
		if self.second_tier != None:
			#pdb.set_trace()
			#print('Adding to 2nd Tier')
			self.second_tier.add_reference(pos)
			
		else:
			self.local[i] = pos
			self.write()

	def total_refs(self):
		x = self.num_refs()
		if self.second_tier :
			x -= 1
			x += self.second_tier.total_refs()
		return x

	def num_refs(self):
		i = Location.REFERENCES
		try:
			i = self.local.index(0)
		except ValueError:
			return Location.REFERENCES + 1 #Ignored as there is no problem when the file is fill
		return i

	def to_string(self):
		bufferr = 3
		data = []
		for item in self.local:
			temp = bufferr - len(str(item))
			data.append(b' ' * temp +Library.int_to_b(item))
		return b'\n'.join(data) + b'\n'

	def write(self):
		Library.write([self.to_string()], [self.pos], self.volume.get_drive())
	
	def get_list(self):
		#pdb.set_trace()
		refs = []
		i = self.num_refs()
		refs.extend(self.local[:i])
		if self.second_tier != None:
			#print('Found 2nd Tier')
			refs.pop()
			refs.extend(self.second_tier.get_list())
		#pdb.set_trace()
		return refs

	def get_location(self):
		return self.pos

	def get_referenced_data(self):
		return self.get_referenced_data_unstriped().rstrip()

	def get_referenced_data_unstriped(self):
		data = b''
		for pos in self.get_list():
			data += self.volume.get_drive().read_block(pos)
		return data
	
	@staticmethod
	def create_from_drive(block_num, volume):
		#pdb.set_trace()
		data = volume.get_drive().read_block(block_num)
		data_list = data.split(b'\n')
		location = Location(block_num, volume)
		data_list.pop()
		no_break = True
		#pdb.set_trace()
		for i, item in enumerate(data_list):
			index = int(item.strip())
			if index != 0:
				location.local[i] = index
			else :
				no_break = False
				break
		if no_break:
			#print('Making 2nd Tier')
			#pdb.set_trace()
			location.second_tier = Location.create_from_drive(location.local[Location.REFERENCES], volume)
		return location
		
		

###################### LIBRARY CLASS ######################

class Library(object):
	
	@staticmethod
	def check_name(name, length):
		Library.check_name_no_length(name)

		if len(name) >= length:
			raise ValueError('Name is too long')

	@staticmethod
	def check_name_no_length(name):
		try:		
			i = name.index(b'\n')
			raise ValueError('Name must not include \\n')
		except:
			pass
		
		if not name.strip():
			raise ValueError('Name Must contain letters or numbers')

	@staticmethod
	def prepare_data(data):
		data_list = []
		length = len(data)
		i = 0
		block_length = Drive.BLK_SIZE
		while length > block_length*i:
			data_list.append(data[i*block_length:(i+1)*block_length])
			i += 1
		spaces = block_length - len(data_list[i-1])
		data_list[i-1] += b' '*spaces
		return data_list
		
	@staticmethod
	def int_to_b(num):
		temp = str(num)
		result = temp.encode()
		return result
	
	@staticmethod
	def write(data, location, drive):
		if len(data) > len(location):
			raise IOError('Not enough locations for data. Needs: ' + str(len(data)) + '   Has: ' +str(len(location)))
		i = 0
		#print('Recording ' + str(len(data)))
		while i < len(data):
			if location[i] > drive.num_blocks():
				raise IOError('Location is out of range of volume\nValue given: ' + str(location[i]))
			if len(data[i]) > Drive.BLK_SIZE:
				raise IOError('data is longer than block size, please use prepare_data function\nSize given: ' + str(len(data[i])))
			drive.write_block(location[i], data[i])
			#print(b'Printed: ' + data[i] + b' @: ' + Library.int_to_b(location[i]))
			i += 1
