
from filesystem import Volume
from drive import Drive
from math import floor
import pdb

'''
string = '  he  llo    '
print(string)
print(string.lstrip())
#print(len(string))
#print(string.decode())
#print(string.encode())
#print(len(string.encode()))

def do_things():
	daa = 7
	dab = str(daa)
	dac = dab.encode()
	return dac
'''
'''
stri = [b'h', b'e', b'l', b'l', b'o']
stri.pop(1)
print(stri)
'''
'''
stri = []
stri.append(b'h')
stri.append(b'e')
stri.append(b'l')
stri.append(b'l')
stri.append(b'o')
stri.append(do_things())
#print(stri[3:10])
result = b'-'.join(stri)
print(result)
'''
'''
blocks = 10
drive_name = 'driveA.txt'
drive = Drive.format(drive_name, blocks)
name = b'new volume test'
volume = Volume.format(drive, name)
volume.unmount()
volume = Volume.mount(drive_name)
'''
'''
length = 63
blocks = blocks = floor(length / 64)
while (len(str(blocks)) + length)/64 >= blocks:
	blocks += 1
print(blocks)
'''
'''
me = b'x---x-x--x'
for i in range(len(me)):
	print(me[i])
'''
'''
print(b'Hello'.isdigit())
print(b'43'.isdigit())
'''
'''
data = [b'3', b'these', b'are words', b'3', b'2', b'x---x', b'x--', b'xx', b'75', b'63']
i = 1
outcome = False
while len(data) > i+1 :
	print('Start: ' + str(len(data)) + ', ' + str(i+1))
	while data[i + 1].isdigit() == outcome:
		data[i] += data[i + 1]
		data.pop(i+1)
	i+=1
	outcome = not outcome
	print('End: ' +str(len(data)) + ', ' + str(i+1))
print(data)
'''
'''
volume = Volume.format(Drive.format('driveD.txt', 8), b'file creation volume')
		#with self.assertRaises(ValueError):
#volume.open(b'fileAB')
file = volume.open(b'fileA')
#		self.assertEqual(0, file.size())
data = b'Hello from fileA'
file.write(0, data)
#		self.assertEqual(len(data), file.size())
file.write(file.size(), data)
#		self.assertEqual(2 * len(data), file.size())
file = volume.open(b'fileB')
data = b'Welcome to fileB'
file.write(50, data)
#		self.assertEqual(50 + len(data), file.size())
volume.unmount()
'''
'''
volume = Volume.format(Drive.format('driveE.txt', 8), b'file read volume')
file = volume.open(b'fileA')
data = b'A different fileA'
file.write(0, data)
#with self.assertRaises(IOError):
#			file.read(30, 1)
#		with self.assertRaises(IOError):
#			file.read(0, 50)
print(file.read(3, 2))
file.write(file.size(), b'Aaargh' * 10)
print(file.read(61, 16))
volume.unmount()
'''
'''
blocks = 10
drive_name = 'driveC.txt'
drive = Drive.format(drive_name, blocks)
drive.disconnect()
#		with self.assertRaises(IOError):
#			Drive.reconnect('badname')
drive = Drive.reconnect(drive_name)
#self.assertEqual(blocks * Drive.BLK_SIZE, drive.num_bytes())
name = b'reconnect volume'
volume = Volume.format(drive, name)
volume.unmount()
#		with self.assertRaises(IOError):
#			Volume.mount('driveZ')
volume = Volume.mount(drive_name)
#self.assertEqual(1, volume.volume_data_blocks())
#self.assertEqual(name, volume.name())
#self.assertEqual(blocks, volume.size())
#self.assertEqual(b'x--------x', volume.bitmap())
#self.assertEqual(9, volume.root_index())
volume.unmount()
'''
'''
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
#self.assertEqual(b'3333', file4.read(0, 4))
file1 = volume.open(b'file1')
#		self.assertEqual(65, file1.size())
#		self.assertEqual(b'0a', file1.read(63, 2))
volume.unmount()
'''
'''
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
#self.assertEqual(b'4444', file4.read(0, 4))
file99 = volume.open(b'file99')
#self.assertEqual(129, file99.size())
#self.assertEqual(b'9a', file99.read(file99.size() - 2, 2))
volume.unmount()
'''
drive_name = 'driveJ.txt'
volume = Volume.format(Drive.format(drive_name, 100), b'file creation volume')
#with self.assertRaises(ValueError):#
volume.open(b'dir/fileAdife')	# incase we ever implement subdirectories
#		with self.assertRaises(ValueError):
#			volume.open(b'fileA\n')
file = volume.open(b'fileA')
#self.assertEqual(0, file.size())
data = b'Hello from fileA' * 10
file.write(0, data)
#self.assertEqual(len(data), file.size())
file.write(file.size(), data)
#self.assertEqual(2 * len(data), file.size())
file = volume.open(b'fileB')
data = b'Welcome to fileB'
file.write(500, data)
#self.assertEqual(500 + len(data), file.size())
volume.unmount()

volume = Volume.mount(drive_name)
#pdb.set_trace()
file = volume.open(b'dir/fileAdife')
file.write(0, b'Good morning')
volume.unmount()

volume = Volume.mount(drive_name)
file = volume.open(b'dir/fileAdife')
print(file.read(0, 5))
volume.unmount()

