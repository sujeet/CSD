#! /usr/bin/python

import getopt
import sys

from Cache import *

file_name = "pinatrace.out"
block_size = 1024
cache_size = 1048576
num_ways = 16
num_sets = 1

def readOptions(argv):
    global file_name, block_size, cache_size, num_ways, num_sets

    help_message = """
Usage:

$ ./cache_simulator.py [options]

-f --trace-file : name of the trace file (mem.trace default)
-b --block-size : block size for the cache in bytes (1K default)
-c --cache-size : size of the cache in bytes (1M default)
-w --ways       : number of ways in the cache (16 default)
"""
    try:
        opts, args = getopt.getopt (argv,
                                    "hb:c:f:m:w:",
                                    ["block-size=",
                                     "cache-size=",
                                     "trace-file=",
                                     "ways="])
    except getopt.GetoptError:
        print help_message
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print help_message
            sys.exit()
        elif opt in ("-f", "--trace-file"):
            file_name = arg
        elif opt in ("-b", "--block-size"):
            try :
                block_size = int(arg)
            except :
                if arg [-1] == 'M' :
                    block_size = int (arg [:-1]) * 1048576
                if arg [-1] == 'K' :
                    block_size = int (arg [:-1]) * 1024
        elif opt in ("-c", "--cache-size"):
            try :
                cache_size = int(arg)
            except :
                if arg [-1] == 'M' :
                    cache_size = int (arg [:-1]) * 1048576
                if arg [-1] == 'K' :
                    cache_size = int (arg [:-1]) * 1024
        elif opt in ("-w", "--ways"):
            num_ways = int(arg)
    
    num_sets =  (cache_size/block_size)/num_ways

def simulate (cache, memtrace) :
    for mode, addr in memtrace :
        if mode == 'R' :
            cache.read (addr)
        elif mode == 'W' :
            cache.write (addr)
    cache.printStats ()


def genMemtrace (filename) :
    """ Returns a list of pairs, [r/w, addr] """
    tracefile = open (filename)
    trace = [tuple(line.strip().split()) for
             line in tracefile.readlines()]
    trace = [pair for pair in trace if len (pair) == 2]
    tracefile.close ()
    return trace
    

if __name__ == "__main__" :
    readOptions (sys.argv [1:])
    memtrace = genMemtrace (file_name)
    sample_addr = memtrace [0][1]
    for cache_type in [Cache,
                       FIFOCache,
                       LRUCache,
                       LFUCache] :
        cache = cache_type (num_sets,
                            num_ways,
                            block_size,
                            sample_addr,
                            write_no_allocate = True)
        simulate (cache, memtrace)
        print '\n\n'
