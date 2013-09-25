'''
Created on 05/09/2013

@author: robert
'''
import unittest
from drive import Drive
from filesystem import Volume

class Test(unittest.TestCase):
	
	def test_new_volume(self):
		blocks = 100
		drive_name = 'driveG.txt'
		disk = Drive.format(drive_name, blocks)
		with self.assertRaises(ValueError):
			Volume.format(disk, b'')
		with self.assertRaises(ValueError):
			Volume.format(disk, b'Volume\nA')
		with self.assertRaises(ValueError):
			Volume.format(disk, b'a' * blocks * Drive.BLK_SIZE)
		name = b'new volume test'
		volume = Volume.format(disk, name)
		self.assertEqual(2, volume.volume_data_blocks())
		self.assertEqual(name, volume.name())
		self.assertEqual(blocks, volume.size())
		self.assertEqual(b'xx-------------------------------------------------------------------------------------------------x', volume.bitmap())
		self.assertEqual(99, volume.root_index())
		volume.unmount()
	
	def test_long_volume_name(self):
		blocks = 100
		drive_name = 'driveH.txt'
		disk = Drive.format(drive_name, blocks)
		name = b'long volume name' * 100
		volume = Volume.format(disk, name)
		self.assertEqual(name, volume.name())
		self.assertEqual(blocks, volume.size())
		self.assertEqual(99, volume.root_index())
		volume.unmount()
	
	def test_reconnect_disk(self):
		blocks = 100
		drive_name = 'driveI.txt'
		disk = Drive.format(drive_name, blocks)
		disk.disconnect()
		with self.assertRaises(IOError):
			Drive.reconnect('badname')
		disk = Drive.reconnect(drive_name)
		self.assertEqual(blocks * Drive.BLK_SIZE, disk.num_bytes())
		name = b'reconnect volume'
		volume = Volume.format(disk, name)
		volume.unmount()
		volume = None
		with self.assertRaises(IOError):
			Volume.mount('driveZ')
		volume = Volume.mount(drive_name)
		self.assertEqual(2, volume.volume_data_blocks())
		self.assertEqual(name, volume.name())
		self.assertEqual(blocks, volume.size())
		self.assertEqual(b'xx-------------------------------------------------------------------------------------------------x', volume.bitmap())
		self.assertEqual(99, volume.root_index())
		volume.unmount()
	
	def test_simple_file_creation(self):
		volume = Volume.format(Drive.format('driveJ.txt', 100), b'file creation volume')
		with self.assertRaises(ValueError):
			volume.open(b'dir/fileA')	# incase we ever implement subdirectories
		with self.assertRaises(ValueError):
			volume.open(b'fileA\n')
		file = volume.open(b'fileA')
		self.assertEqual(0, file.size())
		data = b'Hello from fileA' * 10
		file.write(0, data)
		self.assertEqual(len(data), file.size())
		file.write(file.size(), data)
		self.assertEqual(2 * len(data), file.size())
		file = volume.open(b'fileB')
		data = b'Welcome to fileB'
		file.write(500, data)
		self.assertEqual(500 + len(data), file.size())
		volume.unmount()
	
	def test_file_reads(self):
		volume = Volume.format(Drive.format("driveK.txt", 100), b'file read volume')
		file = volume.open(b'fileA')
		data = b'A different fileA' * 10
		file.write(0, data)
		with self.assertRaises(IOError):
			file.read(300, 1)
		with self.assertRaises(IOError):
			file.read(0, 500)
		self.assertEqual(data, file.read(0, len(data)))
		self.assertEqual(b'if', file.read(71, 2))
		file.write(file.size(), b'Aaargh' * 100)
		self.assertEqual(b'AaarghAaargh', file.read(500, 12))
		volume.unmount()
	
	def test_reconnect_disk_with_files(self):
		drive_name = 'driveL.txt'
		volume = Volume.format(Drive.format(drive_name, 500), b'reconnect with files volume')
		files = []
		for i in range(100):
			name = 'file{:02}'.format(i).encode()
			files.append(volume.open(name))
		for i,file in enumerate(files):
			file.write(0, str(i).encode() * 64)
		files[99].write(files[99].size(), b'a')
		volume.unmount()
		volume = None
		volume = Volume.mount(drive_name)
		file4 = volume.open(b'file04')
		self.assertEqual(b'4444', file4.read(0, 4))
		file99 = volume.open(b'file99')
		self.assertEqual(129, file99.size())
		self.assertEqual(b'9a', file99.read(file99.size() - 2, 2))
		volume.unmount()
		
	def test_write_in_middle(self):
		drive_name = 'driveM.txt'
		volume = Volume.format(Drive.format(drive_name, 500), b'test write in middle')
		file = volume.open(b'file')
		file.write(0, b'123456')
		file.write(3, b'abcd')
		self.assertEqual(b'123abcd', file.read(0,file.size()))
		volume.unmount()

	def test_only_white_space(self):
		drive_name = 'driveN.txt'
		volume = Volume.format(Drive.format(drive_name, 20), b'test whitesapce')
		data = b'\n\t '
		file = volume.open(b'file')
		file.write(0, data * 10)
		volume.unmount()
		volume = None
		volume = Volume.mount(drive_name)
		file = volume.open(b'file')
		self.assertEqual(len(data) * 10, file.size())
		self.assertEqual(data * 10, file.read(0, file.size()))
		volume.unmount()
	
if __name__ == "__main__":
	unittest.main()
