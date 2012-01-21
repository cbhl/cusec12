import time
import defrag_disk
import random
from BaseStrategy import BaseStrategy

class QuickSortBaseStrategy(BaseStrategy):
    def __init__(self):
        self.moves = []

    def scanDisk(self, disk):
        result = {}
        for idx,block in enumerate(disk.blocks):
            if not block.isImmovable():
                if not block.fileId in result:
                    result[block.fileId] = {}
                result[block.fileId][block.fileSequence] = idx
        return result

    def findNextMovableBlock(self, disk, start):
        result = start;
        while result < disk.size and disk.blocks[result].isImmovable():
            result += 1
        if result >= disk.size:
            return None
        return result

    def findLastMovableBlock(self, disk, end):
        result = end-1;
        while result >= 0 and disk.blocks[result].isImmovable():
            result -= 1
        if result < 0:
            return None
        return result

    def desiredLayout(self, files, disk):
        result = self.scanDisk(disk)
        ctr = self.findNextMovableBlock(disk, 0);
        for fileId in range(len(result)):
            for fileSeq in range(len(result[fileId])):
                result[fileId][fileSeq] = ctr
                ctr = self.findNextMovableBlock(disk, ctr+1)
        return result

    def findLastFreeBlock(self, disk, end):
        result = end-1;
        while result >= 0 and (not disk.blocks[result].isFree()):
            result -= 1
        if result < 0:
            return None
        return result

    def move(self, disk, start, end, dest):
        if (start == dest) and (end == (start + 1)):
            return
        moveLine = "{0} {1} {2}".format(start, end, dest)
        print moveLine
        self.moves.append(moveLine)
        move = defrag_disk.Move.fromLine(moveLine)
        disk.move(move)

    def calculate(self, disk):
        initial = self.scanDisk(disk)
        desired = self.desiredLayout(initial,disk)
        # ensure last block is free
        lastMovable = self.findLastMovableBlock(disk, disk.size)
        if not disk.blocks[lastMovable].isFree():
            self.move(disk, lastMovable, lastMovable+1, self.findLastFreeBlock(disk, disk.size))

        # this will be a temp block during most opers
        # TODO: See if this has an averse effect on near-full disks
        secondLastMovable = self.findLastMovableBlock(disk, lastMovable)

        self.quicksort(disk, lastMovable, secondLastMovable, 0, disk.size-1)

        return disk

    def quicksort(self, disk, lastMovable, secondLastMovable, left, right):
        if left < right:
            # choose pivot
            pivot = random.randint(left, right)
            while (disk.blocks[pivot].isImmovable()):
                # pick a better pivot
                pivot = random.randint(left, right)
            
            newPivot = self.partition(disk, lastMovable, secondLastMovable, left, right, pivot)

            self.quicksort(disk, lastMovable, secondLastMovable, left, newPivot-1)
            self.quicksort(disk, lastMovable, secondLastMovable, newPivot+1, right)

    def block_lt(self, disk, i, pivotValueFileId, pivotValueFileSeq):
        if (disk.blocks[i].fileId < pivotValueFileId):
            return True
        elif (disk.blocks[i].fileId == pivotValueFileId) and (disk.blocks[i].fileSequence < pivotValueFileSeq):
            return True
        return False

    def partition(self, disk, lastMovable, secondLastMovable, left, right, pivotIdx):
        pivotValueFileId = disk.blocks[pivotIdx].fileId
        pivotValueFileSeq = disk.blocks[pivotIdx].fileSequence
        if not disk.blocks[lastMovable].isFree():
            self.move(disk, lastMovable, lastMovable+1, self.findLastFreeBlock(disk, disk.size))
        left = self.findNextMovableBlock(disk, left)
        right = self.findLastMovableBlock(disk, right+1)
        self.move(disk, pivotIdx, pivotIdx+1, lastMovable)
        self.move(disk, right, right+1, pivotIdx)

        storeIdx = left

        for i in (n+left for n in range(right-left)):
            if disk.blocks[i].isImmovable():
                continue;
            if self.block_lt(disk, i, pivotValueFileId, pivotValueFileSeq):
                # swap a['i'] and a['storeIdx']
                if not disk.blocks[secondLastMovable].isFree():
                    self.move(disk, secondLastMovable, secondLastMovable+1, self.findLastFreeBlock(disk, secondLastMovable))
                self.move(disk, i, i+1, secondLastMovable)
                self.move(disk, storeIdx, storeIdx+1, i)
                self.move(disk, secondLastMovable, secondLastMovable+1, storeIdx)
                storeIdx = self.findNextMovableBlock(disk, storeIdx+1)

        self.move(disk, storeIdx, storeIdx+1, right)
        self.move(disk, lastMovable, lastMovable+1, storeIdx)

        return storeIdx
        
    def result(self):
        return self.moves
