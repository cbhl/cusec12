#!/usr/bin/env python
'''
Defrag

CUSEC Coding Competition
Waterloo Software Engineering

@author Michael Chang, Alice Yuan, Joshua Kaplin, Aaron Morais
'''

from strategy import *

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='defragments a fictional file system'
        )
    parser.add_argument(
        '--input',
        required=False,
        help='Input file for the disk (if not specified, will read from disk.txt)'
        )
    args = parser.parse_args()

    inputFilename = 'disk.txt' if args.input == None else args.input

    strategies = []
    strategies.append(BaseStrategy.BaseStrategy())

    inputFile = open(inputFilename)

    bestResult = []

    for line in inputFile:
        for strategy in strategies:
            strategy.readline(line)
    for strategy in strategies:
        # FIXME Add timeout
        strategy.calculate()
        result = strategy.result()
        # FIXME evaluate which strategy is best
        if True:
            bestResult = result
    
    # FIXME output in correct format
    print bestResult
