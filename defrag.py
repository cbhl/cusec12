#!/usr/bin/env python
'''
Defrag

CUSEC Coding Competition
Waterloo Software Engineering

@author Michael Chang, Alice Yuan, Joshua Kaplin, Aaron Morais
'''

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
        strategies.append(BaseStrategy.BaseStrategy())
        strategies.append(SleepStrategy.SleepStrategy())
    
        inputFile = open(inputFilename)
    
        bestResult = []
    
        for line in inputFile:
            for strategy in strategies:
                strategy.readline(line)
        for strategy in strategies:
            strategy.calculate()
            result = strategy.result()
            # FIXME evaluate which strategy is best
            if True:
                bestResult = result
    except TimeoutException:
        pass; # fall through to returning the result

    # FIXME output in correct format
    print bestResult

