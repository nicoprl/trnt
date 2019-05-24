#!/usr/bin/python3

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-s')
args = parser.parse_args()

print(args.s)

if args.s:
    print('true')
