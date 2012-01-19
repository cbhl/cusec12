'''
Created on Dec 19, 2011

@author: menard
'''
import unittest
from defrag_scorer import *
from defrag_disk import *

class BlockTest(unittest.TestCase):
    def testImmutable(self):
        block = Block(1, 3)
        with self.assertRaises(AttributeError):
            block.fileId = 12
            
    def testIsFree(self):
        self.assertFalse(Block(1, 2).isFree())
        self.assertTrue(Block(FREE_SPACE, 2).isFree())
        self.assertTrue(Block(FREE_SPACE).isFree())
        
    def testIsImmovable(self):
        self.assertFalse(Block(2, 2).isImmovable())
        self.assertTrue(Block(IMMOVABLE, 2).isImmovable())
        self.assertTrue(Block(IMMOVABLE).isImmovable())
        
    def testInvalidCharacters(self):
        with self.assertRaises(ValueError):
            Block.fromLine("abc 191")
            
    def testInvalidNumberOfTokens(self):
        with self.assertRaises(DiskError):
            Block.fromLine("1 0 191")

class BlockRangeTest(unittest.TestCase):
    def setUp(self):
        self.a = BlockRange(0, 5)
        self.b = BlockRange(4, 7)
        self.c = BlockRange(5, 8)
        self.d = BlockRange(3, 8)
        
    def testImmutable(self):
        with self.assertRaises(AttributeError):
            self.a.begin = 5
            
    def testNonNegative(self):
        with self.assertRaises(TypeError):
            BlockRange(0, -2)
        with self.assertRaises(TypeError):
            BlockRange(-1, 4)
            
    def testAtLeastOne(self):
        with self.assertRaises(TypeError):
            BlockRange(1, 0)
        with self.assertRaises(TypeError):
            BlockRange(1, 1)
        with self.assertRaises(TypeError):
            BlockRange(5, 1)
        
    def testIntersection(self):
        self.assertTrue(self.a.intersects(self.b))
        self.assertTrue(self.b.intersects(self.a))
        
    def testNotIntersecting(self):
        self.assertFalse(self.c.intersects(self.a))
        self.assertFalse(self.a.intersects(self.c))
    
    def testContainingIntersection(self):
        self.assertTrue(self.d.intersects(self.b))
        self.assertTrue(self.b.intersects(self.d))
        
    def testIntersectionBoundaries(self):
        self.assertFalse(BlockRange(0, 1).intersects(BlockRange(1, 2)))
        self.assertFalse(BlockRange(1, 2).intersects(BlockRange(2, 3)))
        self.assertTrue(BlockRange(1, 2).intersects(BlockRange(0, 2)))
        self.assertTrue(BlockRange(1, 2).intersects(BlockRange(1, 2)))
        
    def testContains(self):
        self.assertTrue(self.d.contains(self.b))
        self.assertFalse(self.b.contains(self.d))
        self.assertTrue(self.d.contains(self.d))
        self.assertFalse(self.a.contains(self.b))
        
    def testLength(self):
        self.assertEqual(self.a.length, 5)
        self.assertEqual(self.d.length, 5)
        
class MoveTest(unittest.TestCase):
    def testImmutable(self):
        move = Move(0, 1, 1)
        with self.assertRaises(AttributeError):
            move.sourceRange = BlockRange(2, 3)
    
    def testIntersectingSourceDest(self):
        with self.assertRaises(TypeError):
            Move(0, 2, 1)
            
    def testInvalidCharacters(self):
        with self.assertRaises(ValueError):
            Move.fromLine("abc 191 -ab")
            
    def testInvalidNumberOfTokens(self):
        with self.assertRaises(DiskError):
            Move.fromLine("1 0")

class DiskTest(unittest.TestCase):

    def setUp(self):
        self.disk = Disk()
        self.disk.addBlock(Block(1, 0))
        self.disk.addBlock(Block(1, 1))
        self.disk.addBlock(Block(2, 1))
        self.disk.addBlock(Block(2, 0))
        self.disk.addBlock(Block(FREE_SPACE))
        
    def testSeeksPerFile(self):
        self.assertEqual(self.disk.seeksPerFile(), {1: 1, 2: 2})
        
    def testSeeksPerFile2(self):
        self.disk.addBlock(Block(1, 3))
        self.disk.addBlock(Block(IMMOVABLE))
        self.disk.addBlock(Block(1, 4))
        self.disk.addBlock(Block(2, 0))
        self.disk.addBlock(Block(2, 1))
        self.assertEqual(self.disk.seeksPerFile(), {1: 3, 2: 3})
        
    def testBounds(self):
        self.assertEqual(self.disk.bounds.begin, 0)
        self.assertEqual(self.disk.bounds.end, 5)

    def testPopulateDisk(self):
        self.assertEqual(self.disk.size, 5)
        self.assertEqual(self.disk.getBlock(0), Block(1, 0))
        self.assertEqual(self.disk.getBlock(1), Block(1, 1))
        self.assertEqual(self.disk.getBlock(2), Block(2, 1))
        self.assertEqual(self.disk.getBlock(3), Block(2, 0))
        
    def testEraseOne(self):
        self.assertEqual(self.disk.size, 5)
        self.assertEqual(self.disk.getBlock(0), Block(1, 0))
        
        self.disk.erase(BlockRange(0, 1))
        
        self.assertEqual(self.disk.size, 5)
        self.assertEqual(self.disk.getBlock(0), Block(FREE_SPACE))
        
    def testEraseMany(self):
        self.assertEqual(self.disk.size, 5)
        self.assertEqual(self.disk.getBlock(2), Block(2, 1))
        self.assertEqual(self.disk.getBlock(3), Block(2, 0))
        
        self.disk.erase(BlockRange(2, 4))
        
        self.assertEqual(self.disk.size, 5)
        self.assertEqual(self.disk.getBlock(2), Block(FREE_SPACE))
        self.assertEqual(self.disk.getBlock(3), Block(FREE_SPACE))
        
    def testEraseOutOfBounds(self):
        self.disk.erase(BlockRange(4, 5))
        with self.assertRaises(DiskError):
            self.disk.erase(BlockRange(2, 6))
        with self.assertRaises(DiskError):
            self.disk.erase(BlockRange(5, 6))
            
    def testMoveOne(self):
        self.assertEqual(self.disk.size, 5)
        self.assertEqual(self.disk.getBlock(0), Block(1, 0))
        self.assertEqual(self.disk.getBlock(4), Block(FREE_SPACE))
        
        self.disk.move(Move(0, 1, 4))
        
        self.assertEqual(self.disk.size, 5)
        self.assertEqual(self.disk.getBlock(4), Block(1, 0))
        self.assertEqual(self.disk.getBlock(0), Block(FREE_SPACE))
        
    def testMoveMany(self):
        self.disk.addBlock(Block(FREE_SPACE))
        
        self.assertEqual(self.disk.size, 6)
        self.assertEqual(self.disk.getBlock(0), Block(1, 0))
        self.assertEqual(self.disk.getBlock(1), Block(1, 1))
        self.assertEqual(self.disk.getBlock(4), Block(FREE_SPACE))
        self.assertEqual(self.disk.getBlock(5), Block(FREE_SPACE))
        
        self.disk.move(Move(0, 2, 4))
        
        self.assertEqual(self.disk.size, 6)
        self.assertEqual(self.disk.getBlock(4), Block(1, 0))
        self.assertEqual(self.disk.getBlock(5), Block(1, 1))
        self.assertEqual(self.disk.getBlock(0), Block(FREE_SPACE))
        self.assertEqual(self.disk.getBlock(1), Block(FREE_SPACE))
        
    def testMoveOutOfBounds(self):
        with self.assertRaises(DiskError):
            self.disk.move(Move(0, 2, 4))
            
    def testMoveOverwrite(self):
        with self.assertRaises(DiskError):
            self.disk.move(Move(4, 5, 0))
        with self.assertRaises(DiskError):
            self.disk.move(Move(1, 2, 0))
            
    def testMoveImmovable(self):
        self.disk.addBlock(Block(IMMOVABLE))
        with self.assertRaises(DiskError):
            self.disk.move(Move(5, 6, 4))
    
    def testFree(self):
        self.assertFalse(self.disk.isFree(BlockRange(0, 5)))
        self.assertFalse(self.disk.isFree(BlockRange(0, 3)))
        self.assertTrue(self.disk.isFree(BlockRange(4, 5)))
        self.assertFalse(self.disk.isFree(BlockRange(3, 5)))
            
    def testImmovable(self):
        self.disk.addBlock(Block(IMMOVABLE))
        self.assertFalse(self.disk.isImmovable(BlockRange(0, 5)))
        self.assertFalse(self.disk.isImmovable(BlockRange(3, 5)))
        self.assertTrue(self.disk.isImmovable(BlockRange(3, 6)))
        self.assertTrue(self.disk.isImmovable(BlockRange(5, 6)))
        
    def testFreeRangeIsFree(self):
        self.disk.addBlock(Block(10))
        self.disk.addBlock(Block(11))
        self.disk.addBlock(Block(FREE_SPACE))
        self.disk.addBlock(Block(FREE_SPACE))
        self.disk.addBlock(Block(11))
        self.disk.addBlock(Block(FREE_SPACE))
        self.disk.addBlock(Block(3))
        self.disk.addBlock(Block(4))
        
        for x in range(self.disk.size):
            f = self.disk.findFirstFreeRange(x)
            if f != None:
                self.assertTrue(self.disk.isFree(f))
                
    def testFindAllFreeRanges(self):
        self.disk.addBlock(Block(10))
        self.disk.addBlock(Block(11))
        self.disk.addBlock(Block(FREE_SPACE))
        self.disk.addBlock(Block(FREE_SPACE))
        self.disk.addBlock(Block(11))
        self.disk.addBlock(Block(FREE_SPACE))
        self.disk.addBlock(Block(3))
        self.disk.addBlock(Block(4))
        
        self.assertEqual(self.disk.findAllFreeRanges(), [BlockRange(4,5), BlockRange(7,9), BlockRange(10,11)])
        
    def testReadTrailingSpaces(self):
        lines = ["001   11  ", "101  0   ", "0 0   "]
        
        disk = readDisk(lines)
        
        self.assertEqual(disk.getBlock(0), Block(1, 11))
        self.assertEqual(disk.getBlock(1), Block(101, 0))
        self.assertEqual(disk.getBlock(2), Block(FREE_SPACE))
        self.assertEqual(disk.size, 3)
        
    def testReadLeadingSpaces(self):
        lines = ["   001   11   ", "   101\t0", "   0   0"]
        
        disk = readDisk(lines)
        
        self.assertEqual(disk.getBlock(0), Block(1, 11))
        self.assertEqual(disk.getBlock(1), Block(101, 0))
        self.assertEqual(disk.getBlock(2), Block(FREE_SPACE))
        self.assertEqual(disk.size, 3)
        
    def testReadDiskBlankLine(self):
        lines = ["001 11", "", " \t", "101 0", "0 0", "   "]
        
        disk = readDisk(lines)
        
        self.assertEqual(disk.getBlock(0), Block(1, 11))
        self.assertEqual(disk.getBlock(1), Block(101, 0))
        self.assertEqual(disk.getBlock(2), Block(FREE_SPACE))
        self.assertEqual(disk.size, 3)
        
    def testReadInvalid(self):
        lines = ["001 11", "101 0", "0 0", "0   "]
        
        with self.assertRaises(DiskError):
            readDisk(lines)
        

class ScoringTest(unittest.TestCase):
    def testAvg(self):
        self.assertEqual(avg([1,3,5,7]), 4)
        self.assertEqual(avg([4,5,4,5]), 4.5)
    def testScore(self):
        self.disk = Disk()
        self.disk.addBlock(Block(1, 0))
        self.disk.addBlock(Block(1, 1))
        self.disk.addBlock(Block(2, 1))
        self.disk.addBlock(Block(2, 0))
        self.disk.addBlock(Block(FREE_SPACE))
        self.disk.addBlock(Block(FREE_SPACE))
        
        self.assertEqual(calculateScore(self.disk), 0.5 * 7500.0 + 2500.0)
        
        self.disk = Disk()
        self.disk.addBlock(Block(1, 0))
        self.disk.addBlock(Block(1, 1))
        self.disk.addBlock(Block(2, 0))
        self.disk.addBlock(Block(2, 1))
        self.disk.addBlock(Block(FREE_SPACE))
        self.disk.addBlock(Block(FREE_SPACE))
        
        self.assertEqual(calculateScore(self.disk), 10000.0)
        
        self.disk = Disk()
        self.disk.addBlock(Block(FREE_SPACE))
        self.disk.addBlock(Block(1, 0))
        self.disk.addBlock(Block(1, 1))
        self.disk.addBlock(Block(2, 0))
        self.disk.addBlock(Block(2, 1))
        self.disk.addBlock(Block(FREE_SPACE))
        
        self.assertEqual(calculateScore(self.disk), 7500.0 + 0.25 * 2500.0)
        
    def testDivisionByZeroNoFreeSpace(self):
        self.disk = Disk()
        self.disk.addBlock(Block(1, 0))
        self.disk.addBlock(Block(1, 1))
        self.disk.addBlock(Block(1, 2))
        
        try:
            self.assertEqual(calculateScore(self.disk), 10000.0)
        except ZeroDivisionError:
            self.fail("Divide by zero error")
        
    def testDivisionByZeroNoSeeks(self):
        self.disk = Disk()
        self.disk.addBlock(Block(1, 0))
        self.disk.addBlock(Block(3, 4))
        self.disk.addBlock(Block(2, 1))
        self.disk.addBlock(Block(FREE_SPACE))
        
        try:
            self.assertEqual(calculateScore(self.disk), 10000.0)
        except ZeroDivisionError:
            self.fail("Divide by zero error")
            
    def testOnlyImmovable(self):
        self.disk = Disk()
        self.disk.addBlock(Block(IMMOVABLE, 0))
        self.disk.addBlock(Block(IMMOVABLE, 4))
        self.disk.addBlock(Block(IMMOVABLE, 1))
        
        self.assertEqual(calculateScore(self.disk), 10000.0)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()