'''
Defrag

CUSEC Coding Competition
Waterloo Software Engineering

@author Michael Chang, Alice Yuan, Joshua Kaplin, Aaron Morais
'''

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='defragments a fictional file system')
    parser.add_argument('--input', required=False, help='Input file for the disk (if not specified, will read from disk.txt)'
    args = parser.parse_args()


