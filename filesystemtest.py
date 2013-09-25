'''
Created on 25/08/2013

@author: robert
'''
import unittest
from drive import Drive
from filesystem import A2File, Volume

class Test(unittest.TestCase):

# This test is commented out because it tests the underlying Drive class (and it passes).
#	 def test_drive(self):
#		 blocks = 10
#		 drive = Drive.format('drive.txt', blocks)
#		 self.assertEqual(blocks, drive.num_blocks(), 'number of blocks')
#		 self.assertEqual(blocks * Drive.BLK_SIZE, drive.num_bytes(), 'number of bytes')
#		 data = b'hello world12345'
#		 block_data = b' ' * Drive.BLK_SIZE
#		 block_data = data + block_data[len(data):]
#		 with self.assertRaises(IOError):
#			 drive.write_block(-1, block_data)
#		 with self.assertRaises(IOError):
#			 drive.write_block(blocks, block_data)
#		 with self.assertRaises(ValueError):
#			 drive.write_block(0, b'wrong size')
#		 with self.assertRaises(IOError):
#			 drive.read_block(-1)
#		 with self.assertRaises(IOError):
#			 drive.read_block(blocks)
#		 drive.write_block(0, block_data)
#		 self.assertEqual(block_data, drive.read_block(0), 'written data not read')
#		 drive.write_block(blocks - 1, block_data)
#		 self.assertEqual(block_data, drive.read_block(blocks - 1), 'written data not read')
#		 drive.disconnect()
#		 with self.assertRaises(ValueError):
#			 drive.read_block(0)
#		 drive = Drive.reconnect('drive.txt')
#		 self.assertEqual(block_data, drive.read_block(0), 'written data not read')
#		 drive.disconnect()
		
	def test_new_volume(self):
		blocks = 10
		drive_name = 'driveA.txt'
		drive = Drive.format(drive_name, blocks)
		with self.assertRaises(ValueError):
			Volume.format(drive, b'')
		with self.assertRaises(ValueError):
			Volume.format(drive, b'Volume\nA')
		with self.assertRaises(ValueError):
			Volume.format(drive, b'a' * blocks * Drive.BLK_SIZE)
		name = b'new volume test'
		volume = Volume.format(drive, name)
		self.assertEqual(1, volume.volume_data_blocks())
		self.assertEqual(name, volume.name())
		self.assertEqual(blocks, volume.size())
		self.assertEqual(b'x--------x', volume.bitmap())
		self.assertEqual(9, volume.root_index())
		volume.unmount()
	  
	def test_long_volume_name(self):
		blocks = 10
		drive_name = 'driveB.txt'
		drive = Drive.format(drive_name, blocks)
		name = b'long volume name' * 10
		volume = Volume.format(drive, name)
		self.assertEqual(3, volume.volume_data_blocks())
		self.assertEqual(name, volume.name())
		self.assertEqual(blocks, volume.size())
		self.assertEqual(b'xxx------x', volume.bitmap())
		self.assertEqual(9, volume.root_index())
		volume.unmount()
	   
	def test_reconnect_drive(self):
		blocks = 10
		drive_name = 'driveC.txt'
		drive = Drive.format(drive_name, blocks)
		drive.disconnect()
		with self.assertRaises(IOError):
			Drive.reconnect('badname')
		drive = Drive.reconnect(drive_name)
		self.assertEqual(blocks * Drive.BLK_SIZE, drive.num_bytes())
		name = b'reconnect volume'
		volume = Volume.format(drive, name)
		volume.unmount()
		with self.assertRaises(IOError):
			Volume.mount('driveZ')
		volume = Volume.mount(drive_name)
		self.assertEqual(1, volume.volume_data_blocks())
		self.assertEqual(name, volume.name())
		self.assertEqual(blocks, volume.size())
		self.assertEqual(b'x--------x', volume.bitmap())
		self.assertEqual(9, volume.root_index())
		volume.unmount()
	   
	def test_simple_file_creation(self):
# the Volume didn't call format in the original
		volume = Volume.format(Drive.format('driveD.txt', 8), b'file creation volume')
		with self.assertRaises(ValueError):
			volume.open(b'fileA\n')
		file = volume.open(b'fileA')
		self.assertEqual(0, file.size())
		data = b'Hello from fileA'
		file.write(0, data)
		self.assertEqual(len(data), file.size())
		file.write(file.size(), data)
		self.assertEqual(2 * len(data), file.size())
		file = volume.open(b'fileB')
		data = b'Welcome to fileB'
		file.write(50, data)
		self.assertEqual(50 + len(data), file.size())
		volume.unmount()
	   
	def test_file_reads(self):
		volume = Volume.format(Drive.format('driveE.txt', 8), b'file read volume')
		file = volume.open(b'fileA')
		data = b'A different fileA'
		file.write(0, data)
		with self.assertRaises(IOError):
			file.read(30, 1)
		with self.assertRaises(IOError):
			file.read(0, 50)
		self.assertEqual(data, file.read(0, len(data)))
		self.assertEqual(b'if', file.read(3, 2))
		file.write(file.size(), b'Aaargh' * 10)
		self.assertEqual(b'arghAaarghAaargh', file.read(61, 16))
		volume.unmount()
	   
	def test_reconnect_drive_with_files(self):
		drive_name = 'driveF.txt'
		volume = Volume.format(Drive.format(drive_name, 12), b'reconnect with files volume')
		filenames = [b'file1', b'file2', b'file3', b'file4']
		files = [volume.open(name) for name in filenames]
		for i, file in enumerate(files):
			file.write(0, bytes(str(i).encode()) * 64)
		files[0].write(files[0].size(), b'a')
		volume.unmount()
		volume = Volume.mount(drive_name)
		file4 = volume.open(b'file4')
		self.assertEqual(b'3333', file4.read(0, 4))
		file1 = volume.open(b'file1')
		self.assertEqual(65, file1.size())
		self.assertEqual(b'0a', file1.read(63, 2))
		volume.unmount()

if __name__ == "__main__":
	unittest.main()
