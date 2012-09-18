#! /usr/bin/python

import getopt
# import matplotlib.pyplot as plot
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

-f --trace-file: name of the trace file (mem.trace default)
-b --block-size: block size for the cache in bytes (1K default)
-c --cache-size: size of the cache in bytes (1M default)
-w --ways      : number of ways in the cache (16 default)

Note: All byte numbers should be non-negative powers of 2.
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
            try:
                block_size = int(arg)
            except:
                if arg [-1] == 'M':
                    block_size = int (arg [:-1]) * 1048576
                if arg [-1] == 'K':
                    block_size = int (arg [:-1]) * 1024
        elif opt in ("-c", "--cache-size"):
            try:
                cache_size = int(arg)
            except:
                if arg [-1] == 'M':
                    cache_size = int (arg [:-1]) * 1048576
                if arg [-1] == 'K':
                    cache_size = int (arg [:-1]) * 1024
        elif opt in ("-w", "--ways"):
            num_ways = int(arg)
    
    num_sets =  (cache_size/block_size)/num_ways

def simulate (cache, memtrace):
    for mode, addr in memtrace:
        if mode == 'R':
            cache.read (addr)
        elif mode == 'W':
            cache.write (addr)
    # cache.printStats ()
    
def genMemtrace (filename):
    """ Returns a list of pairs, [r/w, addr] """
    tracefile = open (filename)
    line = tracefile.readline ()
    while line :
        yield tuple (line.strip().split())
        line = tracefile.readline ()
    tracefile.close ()
    # trace = [tuple(line.strip().split()) for
    #          line in tracefile.readlines()]
    # trace = [pair for pair in trace if len (pair) == 2]
    # tracefile.close ()
    # return trace

def genSampleAddr(filename):
    tracefile = open (filename)
    line = tracefile.readline ()
    return line.strip().split() [1]

def ye_old_simulation_attempt ():
    """Simulation attempt with lotsa combos of block size and #ways and whatnot.
    
    Combinatorial Explosion. Hilarity does not ensue.
    """
    cache_list = [Cache, FIFOCache, LRUCache, LFUCache]
    true_false_list = [True, False]
    matrix_size_list = [10, 20]
    # matrix_size_list = range (10, 60, 10) # + [100]
    cache_size_list = [1048576]
    # cache_size_list = [524288, 1048576]
    block_size_list = [16]
    # block_size_list = [1, 4, 16]
    ways_list = [4]
    # ways_list = [1, 4, 16]
    
    # cache_size = cache_size_list[-1]
    # block_size = block_size_list[-1]
    # num_ways = ways_list[-1]
    # for cache_type in cache_list:
    #     cache = cache_type ((cache_size / block_size) / num_ways,
    #                         num_ways,
    #                         block_size,
    #                         sample_addr,
    #                         write_no_allocate = True)
    #     simulate (cache, memtrace)
    #     print cache.getStats ()
    #     print cache.getParameters ()
    #     # print '\n\n'
    
    total = 0
    # Actually this should iterate over memtraces of multiplication of
    # matrices of different sizes and with different blocking factors
    for matrix_size in matrix_size_list:
        # TODO: Use matrix size to read the memtrace for
        # matrix mult of that size
        for cache_type in cache_list:
            for write_no_allocate in true_false_list:
                for cache_size in cache_size_list:
                    for block_size in block_size_list:
                        for num_ways in ways_list:
                            # cache = cache_type (num_sets,
                            #                     num_ways,
                            #                     block_size,
                            #                     sample_addr,
                            #                     write_no_allocate = True)
                            
                            total += 1
                            print '\n'
                            cache = cache_type ((cache_size / block_size) / num_ways,
                                                num_ways,
                                                block_size,
                                                sample_addr,
                                                write_no_allocate = write_no_allocate)
                            simulate (cache, memtrace)
                            # print cache.getStats ()
                            # print cache.getParameters (), '\n'
                            cache.printStats ()

def write_result_to_file (filename, value_list):
    """Write value_list to filename in a comma-separated fashion.
    """
    f = open (filename, 'w')
    f.write ('\n'.join (','.join ((str (key), str (val))) 
                        for key, val in value_list))
    f.close ()

def plot_cache_graphs (cache_list, blocking_factor_list):
    """Plot a graph for each cache in cache_list.

    Each graph will depict stats for all blocking factors in
    blocking_factor_list.
    """
    for cache_type in cache_list:
        plot_graph (cache_type, blocking_factor_list)
        
def plot_graph (cache_type, blocking_factor_list):
    """
    Plot graph 'Conflict Miss Rate vs Matrix Size' for given blocking
    factor.

    Read stats from 'results-<Cache name>-<Blocking factor>.txt' file.
    """
    for blocking_factor in blocking_factor_list:
        filename = 'results-{0}-{1}.txt'.format (cache_type.__name__, blocking_factor)
        f = open (filename, 'r')
        size_miss_rate_list = [(int (line.split (',')[0]),
                                float (line.split (',')[1]))
                                for line in f]
        f.close ()
        x_vals, y_vals = zip (*size_miss_rate_list)
        # print x_vals
        # print y_vals
        plot.plot (x_vals, y_vals, label = 'BF - {0}'.format (blocking_factor))
    plot.xlabel ('Matrix Size')
    plot.ylabel ('Conflict Miss Rate')
    plot.legend (loc = 'upper right')
    plot.title (r'Graph for Block Matrix Multiplication using {0}'.format (
        cache_type.__name__))
    plot.savefig ('results-{0}.png'.format (cache_type.__name__))
    plot.close ()
    
if __name__ == "__main__":
    # readOptions (sys.argv [1:])
    file_name = 'sample-mem-trace.txt'
    memtrace = genMemtrace (file_name)
    sample_addr = genSampleAddr (file_name)

    cache_list = [Cache, FIFOCache, LRUCache, LFUCache]
    true_false_list = [True, False]
    # matrix_size_list = range (10, 60, 10) # + [100]
    cache_size_list = [1048576]
    # cache_size_list = [524288, 1048576]
    block_size_list = [16]
    # block_size_list = [1, 4, 16]
    ways_list = [4]
    # ways_list = [1, 4, 16]

    # TODO: Maybe read this from a file?
    blocking_factor_list = [1, 2, 4, 8, 16]
    matrix_size_list = range (16, 100, 16)

    if len (sys.argv) != 2:
        print 'Enter exactly 1 argument out of:\nplot\nsimulate\nsimulate_all\n'
        exit (1)

    if sys.argv[1] == 'simulate':
        output_dict = {}
        for cache_type in cache_list:
            output_dict[cache_type] = {}
            cache_size = cache_size_list[-1]
            block_size = block_size_list[-1]
            num_ways = ways_list[-1]
            cache = cache_type ((cache_size / block_size) / num_ways,
                                num_ways,
                                block_size,
                                sample_addr,
                                write_no_allocate = True)
            for blocking_factor in blocking_factor_list:
                output_dict[cache_type][blocking_factor] = []
                for matrix_size in matrix_size_list:
                    # TODO: Have actual memtraces in these files
                    memtrace = genMemtrace ('memtrace-{0}-{1}.txt'.format (
                        matrix_size, blocking_factor))
                    simulate (cache, memtrace)
                    output_dict[cache_type][blocking_factor].append (
                        (matrix_size, cache.getHitRate ()))
                # print output_dict[cache_type][blocking_factor]
                write_result_to_file (
                    'results-{0}-{1}.txt'.format (cache_type.__name__, blocking_factor),
                    output_dict[cache_type][blocking_factor])
    elif sys.argv[1] == 'plot':
        plot_cache_graphs (cache_list, blocking_factor_list)
    elif sys.argv[1] == 'simulate_all':
        ye_old_simulation_attempt ()

