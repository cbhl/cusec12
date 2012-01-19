'''
Created on Dec 19, 2011

@author: menard
'''

import defrag_disk

def calculateScore(disk):
    return avgFreeSpaceRangeNormalized(disk) * 2500.0 + avgSeeksPerFileNormalized(disk) * 7500.0

def avgFreeSpaceRangeNormalized(disk):
    lengths = freeRangeLengths(disk.findAllFreeRanges())
    ideal = sum(lengths)
    
    # Prevent a division by 0 below
    if ideal == 0:
        return 1.0
    
    biasFun = lambda x: float(x)**2
    
    biasedLengths = map(biasFun, lengths)
    return (sum(biasedLengths) / float(len(biasedLengths))) / biasFun(ideal)

def avgSeeksPerFileNormalized(disk):
    seeks = disk.seeksPerFile()
    blocks = disk.blocksPerFile()
    
    averageSeeks = avg(seeks.itervalues())
    worstAverageSeeks = avg(blocks.itervalues())
    idealAverageSeeks = 1.0
    
    # Prevents a division by 0 below
    # Less than before worstAverageSeeks of 0 means we have no files
    if worstAverageSeeks <= idealAverageSeeks:
        return 1.0
    
    return (1.0 - (averageSeeks - idealAverageSeeks) / (worstAverageSeeks - idealAverageSeeks))

def avg(iterable):
    output = 0.0
    count = 0.0
    for x in iterable:
        if count != 0.0:
            output = output * count / (count + 1.0) + float(x) / (count + 1.0)
        else:
            output = float(x)
        count = (count + 1.0)
    return output

def freeRangeLengths(freeRanges):
    return map(lambda x: float(x.length), freeRanges)


def loadDisk(filename):
    diskFile = open(filename)
    disk = defrag_disk.readDisk(diskFile)
    diskFile.close()
    return disk

def loadAndExecuteMoves(filename, disk):
    moveFile = open(filename, 'r')
    moveCount = executeMoves(moveFile, disk)
    moveFile.close()
    return moveCount

def executeMoves(lines, disk):
    moveCount = 0
    for line in lines:
        try:
            move = defrag_disk.Move.fromLine(line)
            if move != None:
                disk.move(move)
        except Exception, ex:
            raise Exception("MOVE ERROR At line %d: %s\n%s" % (moveCount+1, line, ex))
        
        moveCount += 1
    
    return moveCount

def saveDisk(disk, filename):
    outFile = open(filename, 'w')
    outFile.write(defrag_disk.formatDisk(disk))
    outFile.close()
    
def printDisk(disk):
    print defrag_disk.formatDisk(disk, headers = True, blockNumbers = True)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Defrag scoring program')
    parser.add_argument('--disk', required=True, help='The fragmented disk file')
    parser.add_argument('--moves', required=True, help='The file containing a list of moves to defragment the disk')
    parser.add_argument('--output', required=False, help='The output file for the defragmented disk (if not specified will go to STDOUT)')
    args = parser.parse_args()
    
    disk = loadDisk(args.disk)
    
    try:
        moveCount = loadAndExecuteMoves(args.moves, disk)
        
        if args.output == None:
            printDisk(disk)
        else:
            saveDisk(disk, args.output)
            
        print "Disk quality: %f" % calculateScore(disk)
        print "Move count: %d" % moveCount
    except Exception, ex:
        print ex
        print "Disk state:"
        printDisk(disk)
        exit()
    