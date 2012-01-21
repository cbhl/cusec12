#!/usr/bin/env python
'''
Defrag

CUSEC Coding Competition
Waterloo Software Engineering

@author Michael Chang, Alice Yuan, Joshua Kaplin, Aaron Morais
'''

import defrag_scorer
from strategy import *

class TimeoutException(Exception):
    pass

if __name__ == '__main__':
    import argparse
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutException()

    parser = argparse.ArgumentParser(
        description='defragments a fictional file system'
        )
    parser.add_argument(
        '--input',
        required=False,
        help='Input file for the disk (if not specified, will read from disk.txt)'
        )
    args = parser.parse_args()

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(295) # five minutes, minus a five second buffer
    # signal.alarm(30)

    try:
    
        inputFilename = 'disk.txt' if args.input == None else args.input

        strategies = []
        #strategies.append(BaseStrategy.BaseStrategy())
        strategies.append(MoveToFrontStrategy.MoveToFrontStrategy())
        strategies.append(MoveToEndStrategy.MoveToEndStrategy())
        strategies.append(QuickSortBaseStrategy.QuickSortBaseStrategy())
        # strategies.append(SleepStrategy.SleepStrategy())

        bestResult = []
        disk = defrag_scorer.loadDisk(inputFilename)
        bestScore = defrag_scorer.calculateScore(disk)
    
        for strategy in strategies:
            disk = defrag_scorer.loadDisk(inputFilename)
            final_disk = strategy.calculate(disk)
            result = strategy.result()
            score = defrag_scorer.calculateScore(final_disk)
            if score > bestScore or len(result) < len(bestResult):
                bestResult = result
                bestScore = score
    except TimeoutException:
        pass; # fall through to returning the result

    # output
    for line in bestResult:
        print line

