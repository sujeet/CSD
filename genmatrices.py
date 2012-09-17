#! /usr/bin/python

import random

MAX_INT = 10

def gen_matrix (matrix_size):
    """Return a randomly-poulated square matrix of size matrix_size.
    """
    return [[random.randint (0, MAX_INT) for j in xrange (matrix_size)]
            for i in xrange (matrix_size)]


def gen_matrix_inputs (matrix_size, num_matrices):
    """Return a list of num_matrices randomly-populated square matrices of size
    matrix_size.
    """
    return [gen_matrix (matrix_size) for i in xrange (num_matrices)]

def write_matrices_to_file (filename, matrices):
    """Write matrices to filename in space-separated format.
    """
    f = open (filename, 'w')
    f.write ('{0}\n'.format (len (matrices[0])))
    for matrix in matrices:
        matrix_str = '\n'.join (' '.join (str (elem) for elem in row)  
                                for row in matrix)
        matrix_str += '\n'
        print matrix_str
        f.write (matrix_str)
    
if __name__ == '__main__':
    # Generate a bunch of matrices for pintool to generate memtraces
    # from.
    blocking_factor_list = [1, 2, 4, 8, 16]
    matrix_size_list = range (16, 100, 16)
    for blocking_factor in blocking_factor_list:
        for matrix_size in matrix_size_list:
            write_matrices_to_file (
                'matrix-input-{0}-{1}.txt'.format (
                    matrix_size, blocking_factor), 
                gen_matrix_inputs (matrix_size, blocking_factor))
