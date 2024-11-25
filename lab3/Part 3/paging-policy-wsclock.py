#! /usr/bin/env python

from __future__ import print_function
import sys
from optparse import OptionParser
import random
import math
import time

# to make Python2 and Python3 act the same -- how dumb
def random_seed(seed):
    try:
        random.seed(seed, version=1)
    except:
        random.seed(seed)
    return

def hfunc(index):
    if index == -1:
        return 'MISS'
    else:
        return 'HIT '

def vfunc(victim):
    if victim == -1:
        return '-'
    else:
        return str(victim)

#
# main program
#
parser = OptionParser()
parser.add_option('-a', '--addresses', default='-1',   help='a set of comma-separated pages to access; -1 means randomly generate',  action='store', type='string', dest='addresses')
parser.add_option('-f', '--addressfile', default='',   help='a file with a bunch of addresses in it',                                action='store', type='string', dest='addressfile')
parser.add_option('-n', '--numaddrs', default='10',    help='if -a (--addresses) is -1, this is the number of addrs to generate',    action='store', type='string', dest='numaddrs')
parser.add_option('-p', '--policy', default='WSClock', help='replacement policy: FIFO, LRU, WSClock',                               action='store', type='string', dest='policy')
parser.add_option('-c', '--cachesize', default='3',    help='size of the page cache, in pages',                                      action='store', type='string', dest='cachesize')
parser.add_option('-m', '--maxpage', default='10',     help='if randomly generating page accesses, this is the max page number',     action='store', type='string', dest='maxpage')
parser.add_option('-s', '--seed', default='0',         help='random number seed',                                                    action='store', type='string', dest='seed')
parser.add_option('-N', '--notrace', default=False,    help='do not print out a detailed trace',                                     action='store_true', dest='notrace')
parser.add_option('-w', '--tau', default=5,            help='time threshold for WSClock algorithm',                                  action='store', type='int', dest='tau')

(options, args) = parser.parse_args()

# Parse options
addresses = str(options.addresses)
numaddrs = int(options.numaddrs)
cachesize = int(options.cachesize)
seed = int(options.seed)
maxpage = int(options.maxpage)
policy = str(options.policy)
tau = int(options.tau)
notrace = options.notrace

random_seed(seed)

# Generate or load address list
addrList = []
if addresses == '-1':
    for _ in range(numaddrs):
        addrList.append(int(maxpage * random.random()))
else:
    addrList = list(map(int, addresses.split(',')))

# Initialize cache and statistics
memory = []
ref_bits = {}
access_time = {}
hits = 0
misses = 0
clock_pointer = 0
time_now = 0

def wsclock_algorithm(page):
    global clock_pointer, time_now
    scanned_pages = 0

    while scanned_pages < len(memory):
        candidate = memory[clock_pointer]
        print(f"Scanning page {candidate}, ref_bit={ref_bits[candidate]}, time_since_access={time_now - access_time[candidate]}")  # Діагностика

        if ref_bits[candidate] == 1:
            ref_bits[candidate] = 0
        elif (time_now - access_time[candidate]) > tau:
            print(f"Evicting page {candidate}")
            del ref_bits[candidate]
            del access_time[candidate]
            return memory.pop(clock_pointer)

        clock_pointer = (clock_pointer + 1) % cachesize
        scanned_pages += 1

    victim = memory[clock_pointer]
    print(f"Evicting page {victim} as last resort")
    del ref_bits[victim]
    del access_time[victim]
    return memory.pop(clock_pointer)


# Simulate the policy
for page in addrList:
    time_now += 1
    if page in memory:
        hits += 1
        ref_bits[page] = 1
        access_time[page] = time_now
        if not notrace:
            print(f"Access: {page} HIT State of Memory: {memory}")
    else:
        misses += 1
        if len(memory) < cachesize:
            memory.append(page)
        else:
            victim = wsclock_algorithm(page)
            if not notrace:
                print(f"Replaced: {victim}")
            memory.append(page)
        ref_bits[page] = 1
        access_time[page] = time_now
        if not notrace:
            print(f"Access: {page} MISS State of Memory: {memory}")

# Print final statistics
print(f"FINAL STATS: Hits: {hits} Misses: {misses} Hit Rate: {100 * hits / (hits + misses):.2f}%")
