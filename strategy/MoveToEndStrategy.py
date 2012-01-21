import time
import defrag_disk
from BaseStrategy import BaseStrategy

class MoveToEndStrategy(BaseStrategy):
    def __init__(self):
        self.moves = []

    def findLastFreeRange(self, disk, end):
        if end > disk.size:
            return None

        while True:
            if end <= 0:
                return None
            if disk.blocks[end-1].isFree():
                break
            end -= 1

        start = end - 1

        while start > 0 and disk.blocks[start-1].isFree():
            start -= 1

        return defrag_disk.BlockRange(start, end)

    def findLastDataRange(self, disk, end):
        if end > disk.size:
            return None

        while True:
            if end <= 0:
                return None
            if (not (disk.blocks[end-1].isFree() or disk.blocks[end-1].isImmovable())):
                break
            end -= 1

        start = end - 1

        while start > 0 and (not
            (disk.blocks[start-1].isFree() or disk.blocks[start-1].isImmovable())):
            start -= 1

        return defrag_disk.BlockRange(start, end)

    def calculate(self, disk):
        while True:
            freeRange = self.findLastFreeRange(disk, disk.size)
            if freeRange is None or freeRange.begin <= 0:
                return disk
            else:
                dataRange = self.findLastDataRange(disk, freeRange.begin)
                if dataRange is None:
                    return disk
                if dataRange.length > freeRange.length:
                    dataRange = defrag_disk.BlockRange(dataRange.end - freeRange.length, dataRange.end)
                moveLine = "{0} {1} {2}".format(dataRange.begin, dataRange.end, freeRange.end - dataRange.length)
                self.moves.append(moveLine)
                # calculate move
                move = defrag_disk.Move.fromLine(moveLine)
                disk.move(move)
        
    def result(self):
        return self.moves
