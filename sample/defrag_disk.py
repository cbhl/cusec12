'''
Created on Jan 13, 2012

@author: menard
'''

import itertools

FREE_SPACE = 0
IMMOVABLE = -1

def readDisk(lines):
    disk = Disk()
    
    for line in lines:
        block = Block.fromLine(line)
        if block != None:
            disk.addBlock(block)
    
    return disk

def formatDisk(disk, headers = False, blockNumbers = False):
    output = ""
    if headers:
        output += "# BLOCK:   FILE    SEQ\n"
    
    i = 0
    for b in disk.blocks:
        if blockNumbers:
            output += "#%06i: %s\n" % (i, b)
        else:
            output += str(b) + "\n"
        i += 1
        
    return output

class Disk:
    def __init__(self):
        self.blocks = list()
    
    def addBlock(self, block):
        self.blocks.append(block)
        
    def move(self, move):
        self.copy(move)
        self.erase(move.sourceRange)
    
    def copy(self, move):
        if not self.bounds.contains(move.sourceRange):
            raise DiskError("Move source is out of bounds")
        
        if not self.bounds.contains(move.destinationRange):
            raise DiskError("Move destination is out of bounds")
        
        if not self.isFree(move.destinationRange):
            raise DiskError("Move destination ("+str(move.destinationRange)+") is not free")
        
        self.__copy(move)
            
    def __copy(self, move):
        blocksToMove = self.blocks[move.sourceRange.begin : move.sourceRange.end]
        
        destination = move.destinationRange.begin
        for block in blocksToMove:
            self.blocks[destination] = block
            destination += 1
        
    def erase(self, eraseRange):
        if not self.bounds.contains(eraseRange):
            raise DiskError("Erase range is out of bounds")
        
        if self.isImmovable(eraseRange):
            raise DiskError("Erase range is immovable and cannot be erased")
        
        self.__erase(eraseRange)
    
    def __erase(self, eraseRange):
        self.blocks[eraseRange.begin : eraseRange.end] = itertools.repeat(Block(FREE_SPACE), eraseRange.length)
        
    def findAllFreeRanges(self):
        freeList = list()
        
        free = self.findFirstFreeRange(0)
        while free != None:
            freeList.append(free)
            free = self.findFirstFreeRange(free.end)
            
        return freeList
    
    def findFirstFreeRange(self, start):
        if start < 0:
            return None
        
        while True:
            if start >= self.size:
                return None
            if self.blocks[start].isFree():
                break   
            start += 1
            
        end = start + 1
        
        while end < self.size and self.blocks[end].isFree():
            end += 1
            
        return BlockRange(start, end)
    
    def seeksPerFile(self):
        seeks = dict()
        
        prevBlock = None
        for block in self.blocks:
            if block.isFree() or block.isImmovable():
                prevBlock = None
            else:
                if self.__isSeek(block, prevBlock):
                    self.__incrementFileCount(seeks, block.fileId)
                prevBlock = block
                
        return seeks
    
    def __isSeek(self, block, prevBlock):
        if prevBlock == None:
            return True
        
        expectedFile = prevBlock.fileId
        expectedSequence = prevBlock.fileSequence + 1
        return block.fileId != expectedFile or block.fileSequence != expectedSequence
    
    def blocksPerFile(self):
        blocks = dict()
        
        for block in self.blocks:
            if block.isFree() or block.isImmovable():
                continue
            
            self.__incrementFileCount(blocks, block.fileId)
                
        return blocks
    
    def __incrementFileCount(self, files, fileId):
        if fileId not in files:
            files[fileId] = 1
        else:
            files[fileId] += 1
            
    def isFree(self, freeRange):
        for block in self.blocks[freeRange.begin : freeRange.end]:
            if not block.isFree():
                return False
        return True
    
    def isImmovable(self, immovableRange):
        for block in self.blocks[immovableRange.begin : immovableRange.end]:
            if block.isImmovable():
                return True
        return False
    
    @property  
    def size(self):
        return len(self.blocks)
    
    @property
    def bounds(self):
        return BlockRange(0, self.size)
    
    def getBlock(self, position):
        return self.blocks[position]

class Move(tuple):
    def __new__(cls, sourceBegin, sourceEnd, destination):
        sourceRange = BlockRange(sourceBegin, sourceEnd)
        destinationRange = BlockRange(destination, destination + (sourceEnd-sourceBegin))
        
        if sourceRange.intersects(destinationRange):
            raise TypeError("Move source and destination cannot intersect")
        
        return tuple.__new__(cls, (sourceRange, destinationRange))
    
    @classmethod
    def fromLine(cls, line):
        tokens = line.split()
        if len(tokens) == 0:
            return None
        if len(tokens) != 3:
            raise DiskError("Invalid Move Format: "+line)
        move = Move(int(tokens[0]), int(tokens[1]), int(tokens[2]))
        return move
    
    @property
    def sourceRange(self):
        return self[0]
    
    @property
    def destinationRange(self):
        return self[1]
    
    def __str__(self):
        return "%06d %06d %06d" % (self.sourceRange.begin, self.sourceRange.end, self.destinationRange.begin)

class BlockRange(tuple):
    def __new__(cls, inclusiveBegin, exclusiveEnd):
        if inclusiveBegin < 0 or exclusiveEnd < 0:
            raise TypeError("BlockRange begin or end cannot be negative")
        if inclusiveBegin >= exclusiveEnd:
            raise TypeError("BlockRange must have a length of at least one")
        
        return tuple.__new__(cls, (inclusiveBegin, exclusiveEnd))
    
    def intersects(self, otherRange):
        return not(otherRange.end <= self.begin or otherRange.begin >= self.end)
    
    def contains(self, otherRange):
        return self.begin <= otherRange.begin and self.end >= otherRange.end
    
    @property
    def begin(self):
        return self[0]
    
    @property
    def end(self):
        return self[1]
    
    @property
    def length(self):
        return self[1] - self[0]
    
    def __str__(self):
        return "%d:%d" % (self.begin, self.end)
    
class Block(tuple):
    
    def __new__(cls, fileId, fileSequence = 0):
        if fileId < 1 and fileId != FREE_SPACE and fileId != IMMOVABLE:
            raise TypeError("Invalid Block fileId %d" % fileId)
        if fileSequence < 0:
            raise TypeError("Block cannot have negative file sequence number")
        
        return tuple.__new__(cls, (fileId, fileSequence))
    
    @classmethod
    def fromLine(cls, line):
        tokens = line.split()
        if len(tokens) == 0:
            return None
        if len(tokens) != 2:
            raise DiskError("Invalid Block Format: "+line)
        block = Block(int(tokens[0]), int(tokens[1]))
        return block
    
    @property  
    def fileId(self):
        return self[0]
    
    @property
    def fileSequence(self):
        return self[1]
    
    def isFree(self):
        return self.fileId == FREE_SPACE
    
    def isImmovable(self):
        return self.fileId == IMMOVABLE
    
    def __str__(self):
        return "%6d %6d" % (self.fileId, self.fileSequence)

class DiskError(Exception):
    pass
