'''
Created on 27/08/2013
The underlying Drive class which actually stores all data in a real text file.
USE AS IS.
NO MODIFICATION WITHOUT PERMISSION.
@author: robert
'''

import os

class Drive(object):
    '''
    A drive.
    You can be sure that all drives have at least 3 blocks and less than 1000 blocks.
    '''

    BLK_SIZE = 64
    EMPTY_BLK = b' ' * BLK_SIZE
    SEPARATOR = b'\n**    **\n'

    def __init__(self, name, size):
        '''
        "name" is the real file which stores this Drive on the disk.
        "size" is the number of blocks.
        '''
        self.name = name
        self.size = size
    
    @staticmethod   
    def format(name, size):
        '''
        Creates a Drive object.
        Associates it with underlying real file.
        And writes the block information, including block separators, to this file.
        '''
        drive = Drive(name, size)
        drive.file = open(name, mode='w+b')
        for n in range(size):
            separator = Drive.SEPARATOR[:3] + str(n).encode().rjust(3) + Drive.SEPARATOR[6:]
            drive.file.write(Drive.EMPTY_BLK + separator)
        drive.file.flush()
        return drive
    
    @staticmethod
    def reconnect(name):
        '''
        Reconnects an existing real file as a Drive object.
        '''
        if not os.path.exists(name):
            raise IOError('file does not exist')
        size = os.path.getsize(name)
        drive = Drive(name, size // (Drive.BLK_SIZE + len(Drive.SEPARATOR)))
        drive.file = open(name, mode='r+b')
        return drive
    
    def disconnect(self):
        '''
        Shuts the underlying real file down.
        '''
        self.file.close()
    
    def num_blocks(self):
        '''
        Returns the number of blocks in the drive.
        '''
        return self.size
    
    def num_bytes(self):
        '''
        Returns the number of "usable" bytes in the drive.
        '''
        return self.size * Drive.BLK_SIZE
    
    def write_block(self, n, data):
        '''
        Writes "data" to block "n" of the drive.
        '''
        if n < 0 or n >= self.size:
            raise IOError('block out of range')
        if len(data) != Drive.BLK_SIZE:
            raise ValueError('data not block size')
        self.file.seek(n * (Drive.BLK_SIZE + len(Drive.SEPARATOR)))
        written = self.file.write(data)
        if written != Drive.BLK_SIZE:
            raise IOError('incomplete block written')
        
    def read_block(self, n):
        '''
        Reads and returns block "n" from the drive.
        '''
        if n < 0 or n >= self.size:
            raise IOError('block out of range')
        self.file.seek(n * (Drive.BLK_SIZE + len(Drive.SEPARATOR)))
        return self.file.read(Drive.BLK_SIZE)
