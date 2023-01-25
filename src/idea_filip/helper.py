from scipy.sparse import random
from scipy import stats
from numpy.random import default_rng
import numpy as np

def generate_random_matrix(N, K):
    rng = default_rng()
    rvs = stats.poisson(5, loc=5).rvs
    S = random(N, K, density=0.1, random_state=rng, data_rvs=rvs)
    return S

def get_grid_format(A, nnz, N, K, Nt, Kt):
    px = N//Nt
    py = K//Kt

    A_i = np.zeros(nnz)
    A_j = np.zeros(nnz)
    A_val = np.zeros(nnz)
    A_grid_ptr = np.zeros(px*py)

    idx = 0
    # iterate all grids
    for x in range(px):
        for y in range(py):
            A_grid_ptr[x*px+y] = idx
            # iterate the grid itself
            for i in range(Nt):
                for j in range(Kt):
                    row = x*Nt + i
                    col = y*Kt + j
                    
                    if(A[row,col] != 0):
                        A_i[idx] = row
                        A_j[idx] = col
                        A_val[idx] = A[row,col]
                        idx+=1

    return A_i, A_j, A_val, A_grid_ptr

def build_matrix_from_grid(N, K, A_i, A_j, A_val, A_grid_ptr):
    A = np.zeros((N,K))
    for i in range(len(A_val)):
        row = A_i[i]
        col = A_j[i]
        A[int(row), int(col)] = A_val[i]

    return A



# ==== for testing: =====
N = 32
K = 16
Nt = 8
Kt = 4

S = generate_random_matrix(N,K)
A = S.A
nnz = S.count_nonzero()

#print(A)

A_i, A_j, A_val, A_grid_ptr = get_grid_format(A, nnz, N, K, Nt, Kt)

A_built = build_matrix_from_grid(N,K, A_i, A_j, A_val, A_grid_ptr)

np.testing.assert_equal(A, A_built)

