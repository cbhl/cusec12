'''
Created on Jan 13, 2012

@author: menard
'''

from defrag_disk import *
import random

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Disk generator program')
    parser.add_argument('--size', required=True, type=int, help='The size of the disk to generate')
    parser.add_argument('--pctfree', required=False, default=50, type=float, help='The free space percentage')
    parser.add_argument('--pctimmovable', required=False, default=5, type=float, help='The free space percentage')
    parser.add_argument('--minfilesize', required=False, type=int, help='The free space percentage')
    parser.add_argument('--maxfilesize', required=False, type=int, help='The free space percentage')
    parser.add_argument('--output', required=False, help='The output file for the disk (if not specified will go to STDOUT)')
    args = parser.parse_args()
    
    freeCount = int(args.pctfree / 100.0 * args.size)
    immovableCount = int(args.pctimmovable / 100.0 * args.size)
    fileCount = args.size - freeCount - immovableCount
    
    if args.minfilesize == None:
        args.minfilesize = 1
    if args.maxfilesize == None:
        args.maxfilesize = fileCount
        
    if args.minfilesize < 1:
        print "minfilesize must be greater than 1"
        exit(1)
        
    if args.maxfilesize < 1:
        print "maxfilesize must be greater than 1"
        exit(1)
    
    if fileCount < 0:
        print "Incompatible free and immovable percentages"
        exit(1)
    
    disk = Disk()
    
    while immovableCount > 0:
        disk.addBlock(Block(IMMOVABLE))
        immovableCount -= 1
        
    while freeCount > 0:
        disk.addBlock(Block(FREE_SPACE))
        freeCount -= 1
    
    fileId = 1
    while fileCount > 0:
        fileSize = random.randint(args.minfilesize, args.maxfilesize)
        fileSize = min(fileSize, fileCount)
        for seq in range(fileSize):
            disk.addBlock(Block(fileId, seq))
        fileId += 1
        fileCount -= fileSize
        
    random.shuffle(disk.blocks)
    
    if args.output == None:
        print formatDisk(disk)
    else:
        outputFile = open(args.output, 'w')
        outputFile.write(formatDisk(disk))
        outputFile.close()