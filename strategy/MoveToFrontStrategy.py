import time
import defrag_disk
from BaseStrategy import BaseStrategy

class MoveToFrontStrategy(BaseStrategy):
    def __init__(self):
        self.moves = []

    def calculate(self, disk):
        while True:
            freeRange = disk.findFirstFreeRange(0)
            if freeRange.end >= disk.size:
                return disk
            else:
                dataStart = freeRange.end
                while dataStart < disk.size and (disk.blocks[dataStart].isFree() or disk.blocks[dataStart].isImmovable()):
                    dataStart += 1
                if dataStart >= disk.size:
                    return disk
                dataEnd = dataStart
                while dataEnd < disk.size and (not (disk.blocks[dataEnd].isFree() or disk.blocks[dataEnd].isImmovable())):
                    dataEnd += 1
                if (dataEnd - dataStart) > freeRange.length:
                    dataEnd = dataStart + freeRange.length
                moveLine = "{0} {1} {2}".format(dataStart, dataEnd, freeRange.begin)
                self.moves.append(moveLine)
                # calculate move
                move = defrag_disk.Move.fromLine(moveLine)
                disk.move(move)
        
    def result(self):
        return self.moves
