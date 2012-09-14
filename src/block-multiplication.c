/*
  Program to calculate matrix product using block matrix
  multiplication method.
*/

#include <math.h>
#include <malloc.h>
#include <stdio.h>
#include <stdlib.h>

int **allocate_matrix (int num_rows, int num_cols){
    int **matrix = (int **) malloc(num_rows * sizeof(int *));
    if (!matrix){
        fprintf (stderr, "Allocating pointer array failed.\nExiting...\n");
        exit (1);
    }
    int i;
    for(i = 0; i < num_rows; i++){
        matrix[i] = (int *)malloc(num_cols * sizeof(int));
        if (!matrix[i]){
            fprintf (stderr, "Allocating row failed.\nExiting...\n");
            exit (1);
        }
    }
    return matrix;
}

/**
 * Return the matrix product of square matrices A and B.
 * The multiplication is done using block matrix multiplication method.
 * The total number of multiplications remains the same as in the
 * naive method but the number of memory accesses goes down.
 *
 * Assumptions: blocks are square matrices too, of size matrix_size /
 * num_blocks.
 *
 * num_blocks: number of blocks one row will be divided into
 */
int **block_matrix_product(int **A,
                 int **B,
                 int matrix_size,
                 int num_blocks)
{
    int **C;
    int block_size = matrix_size / num_blocks;
    int scaled_i, scaled_j, scaled_k;
    C = allocate_matrix (matrix_size, matrix_size);

    int i, j, k, temp, sub_i, sub_j, sub_k;
    for (i = 0; i < num_blocks; i++){
        for (j = 0; j < num_blocks; j++){
            /* C_i_j: The submatrix at (i, j) */
            for (k = 0; k < num_blocks; k++){
                /* C_i_j = summation-k { A_i_k * B_k_j }
                   (multiplication of submatrices) */
                scaled_i = i * block_size;
                scaled_j = j * block_size;
                scaled_k = k * block_size;
                for (sub_i = 0; sub_i < block_size; sub_i++){
                    for (sub_j = 0; sub_j < block_size; sub_j++){
                        temp = 0;
                        for (sub_k = 0; sub_k < block_size; sub_k++){
                            temp += A[scaled_i + sub_i][scaled_k + sub_k]
                                    * B[scaled_k + sub_k][scaled_j + sub_j];
                        }
                        /* TODO: Maybe store the submatrix result in a
                           temp array and then write to C_i_j */
                        C[scaled_i + sub_i][scaled_j + sub_j] += temp;
                    }
                }
            }

        }
    }
    return C;
}

/*
 * Print matrix.
 */
void print_matrix(int **A, int num_rows, int num_cols)
{
    int i,j;
    
    for (i = 0; i < num_rows; i++){
        for (j = 0; j < num_cols; j++){
            printf("%3d\t", A[i][j]);
        }
        printf ("\n");
    }
}

int main(int argc, char *argv[])
{
    if (argc != 2){
        printf ("Format: %s blocking_factor\n", argv[0]);
        exit (1);
    }

    int matrix_size;
    /* Number of blocks in one row */
    int blocking_factor;
    int i, j;
    int **A, **B;

    blocking_factor = atoi (argv[1]);
    printf ("blocking_factor: %d\n", blocking_factor);

    scanf ("%d", &matrix_size);
    printf ("matrix_size: %d\n", matrix_size);

    if (matrix_size % blocking_factor != 0){
        fprintf (stderr, "Matrix size should be a multiple of blocking factor\n");
        exit (1);
    }

    A = allocate_matrix (matrix_size, matrix_size);
    B = allocate_matrix (matrix_size, matrix_size);

    for (i = 0; i < matrix_size; i++){
        for (j = 0; j < matrix_size; j++){
            scanf ("%d", &A[i][j]);
        }
    }

    for (i = 0; i < matrix_size; i++){
        for (j = 0; j < matrix_size; j++){
            scanf ("%d", &B[i][j]);
        }
    }

    printf ("First matrix:\n");
    print_matrix (A, matrix_size, matrix_size);
    printf ("Second matrix:\n");
    print_matrix (B, matrix_size, matrix_size);

    int **C = block_matrix_product (A, B, matrix_size, blocking_factor);
    printf ("Product:\n");
    print_matrix (C, matrix_size, matrix_size);
    return 0;
}


