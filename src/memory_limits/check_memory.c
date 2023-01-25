#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h> 
#include <stdbool.h>

/**
 * Prints matrix elements seperated by '\t' and '\n' to stdout
 * @param matrix pointer to matrix (nxm)
 * @param n row dimension of matrix 
 * @param m column dimension of matrix 
 */
void print_matrix(double *matrix, int n, int m) {
    for (int row=0; row < n; row++) {
        for (int column=0; column < m; column++) {
            printf("%.2f\t", matrix[row * m + column]);
        }
        printf("\n");
    }
}

/**
 * Generates a random sparse matrix of doubles 
 * @param density density in percent
 * @param n row dimension of matrix 
 * @param m column dimension of matrix 
 */
double* generate_sparse_matrix(int density, int n, int m){ 
    int i, j;
    int total_elements = n * m;
    int non_zero_elements = (int)(density * total_elements / 100.0);

    // Seed the random number generator
    // For reproducability, we set the seed to 0
    srand(0);

    // Allocate memory for the matrix
    double* matrix = (double *)calloc(total_elements, sizeof(double));

    // Generate random non-zero elements
    for (i = 0; i < non_zero_elements; i++) {
        int index;
        do {
            index = rand() % total_elements;
        } while (matrix[index] != 0);
        matrix[index] = (double)rand()/RAND_MAX;  // Set the non-zero element
    }

    return matrix;
} 

/**
 * Reads a csv double matrix separated by ',' and returns a C double matrix containing the values
 * @param filename name of the file to be read
 * @param n row dimension of matrix 
 * @param m column dimension of matrix 
 */
double* read_csv_matrix(char* filename, int n, int m){
    FILE* fp;
    fp = fopen(filename, "r");

    if (fp == NULL) {
        printf("Error opening file!\n");
        exit(1);
    }

    double* output = malloc(n * m * sizeof(double));

    // allocate memory
    char *buffer;
    size_t size = 4096;
    int bytes_read;
    buffer = (char *) malloc (size);
    int idx = 0;
    
    while (1) {
        bytes_read = getline(&buffer, &size, fp);

        if(bytes_read == -1){
            break;
        }

        const int curr_bytes = bytes_read;
        char buf[curr_bytes];


        // have to copy bytes, because strtok may modify the scaling buffer (=bad)
        memcpy(buf, buffer, curr_bytes);

        // If you need all the values in a row
        char *token = strtok(buf, ",");
        while (token) { 
            char *ptr;
            double n = strtod(token, &ptr);
            
            output[idx] = n;
            idx++;
            token = strtok(NULL, ",");
        }
    }
    
    return output;
}

/**
 * Writes a matrix of doubles into the specified file
 * @param matrix a matrix of doubles
 * @param rows row dimension of matrix 
 * @param cols column dimension of matrix 
 * @param filename filename to write to 
 */
void write_csv_matrix(double* matrix, int rows, int cols, char* filename) {
    FILE* fp;
    fp = fopen(filename, "w");
    if (fp == NULL) {
        printf("Error opening file!\n");
        exit(1);
    }
    // Write the matrix to the file
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            fprintf(fp, "%f", matrix[i*cols + j]);
            if (j < cols - 1) {
                fprintf(fp, ",");
            }
        }
        fprintf(fp, "\n");
    }
    fclose(fp);
}

/**
 * Retrieves relevant parameters for the memory calculation of the CSC formatted matrix
 * @param matrix double matrix
 * @param n row dimension of matrix
 * @param m column dimension of matrix 
 * @param Px grid dimension column
 * @param Py grid dimension row
 * @param A_len Largest A_len of any submatrix 
 * @param A_rowidx_len Largest A_rowidx_len of any submatrix 
 * @param A_colptr_len Largest A_colptr_len of any submatrix 
 */
void retrieve_grid_csc_grid_params(double* matrix, int n, int m, int Px, int Py, int* A_len, int* A_rowidx_len, int* A_colptr_len){

    int grid_col_idx;
    int grid_row_idx;


    // If grid dimension do not align, extend by one
    int grid_height = n % Py == 0 ? n / Py : n/Py + 1;
    int grid_width = m % Px == 0 ? m / Px : m/Px + 1;

    int local_A_len, max_A_len, local_rowidx_len, max_rowidx_len, local_colptr_len, max_colptr_len;
    local_A_len = max_A_len = local_rowidx_len = max_rowidx_len = local_colptr_len = max_colptr_len = 0;

    // Traverse gridwise (from left to right)
    for(int i=0; i<Py; i++){
        for(int j=0; j<Px; j++){
            
            local_A_len = local_rowidx_len = local_colptr_len = 0;

            // Here, we traverse inside the grid
            for(grid_col_idx = 0; grid_col_idx < grid_width; grid_col_idx++){
                
                // check column bounds
                int global_col = grid_width*j + grid_col_idx;
                if(global_col >= m){
                    break;
                }

                local_colptr_len++;
                

                for(grid_row_idx = 0; grid_row_idx < grid_height; grid_row_idx++){
                    
                    // check row bounds
                    int global_row = grid_height*i + grid_row_idx;
                    if(global_row >= n){
                        break;
                    }

                    // check if we have a non-zero value
                    int index = global_row*m + global_col;
                    
                    if(matrix[index] != 0){
                        local_A_len++;
                        local_rowidx_len++;
                    }

                }
                
            }

            // write final amt
            local_colptr_len++;

            // Update max values
            if(local_A_len > max_A_len)
                max_A_len = local_A_len;

            if(local_colptr_len > max_colptr_len)
                max_colptr_len = local_colptr_len;

            if(local_rowidx_len > max_rowidx_len)
                max_rowidx_len = local_rowidx_len;
        }
    }

    *A_len = max_A_len;
    *A_colptr_len = max_colptr_len;
    *A_rowidx_len = max_rowidx_len;
}


/**
 * Retrieves relevant parameters for the memory calculation of the CSR formatted matrix
 * @param matrix double matrix
 * @param n row dimension of matrix
 * @param m column dimension of matrix 
 * @param Px grid dimension column
 * @param Py grid dimension row
 * @param A_len Largest A_len of any submatrix 
 * @param A_colidx_len Largest A_rowidx_len of any submatrix 
 * @param A_rowptr_len Largest A_colptr_len of any submatrix 
 */
void retrieve_to_grid_csr_grid_params(double* matrix, int n, int m, int Px, int Py, int* A_len, int* A_colidx_len, int* A_rowptr_len){

    int grid_col_idx;
    int grid_row_idx;

    // If grid dimension do not align, extend by one
    int grid_height = n % Py == 0 ? n / Py : n/Py + 1;
    int grid_width = m % Px == 0 ? m / Px : m/Px + 1;

    int local_A_len, max_A_len, local_colidx_len, max_colidx_len, local_rowptr_len, max_rowptr_len;
    local_A_len = max_A_len = local_colidx_len = max_colidx_len = local_rowptr_len = max_rowptr_len = 0;

    // Traverse gridwise (from left to right)
    for(int i=0; i<Py; i++){
        for(int j=0; j<Px; j++){
            
            local_A_len = local_colidx_len = local_rowptr_len = 0;

            // Here, we traverse inside the grid
            for(grid_row_idx = 0; grid_row_idx < grid_height; grid_row_idx++){
                
                // check row bounds
                int global_row = grid_height*i + grid_row_idx;
                if(global_row >= n){
                    break;
                }


                // write row pointer
                local_rowptr_len++;
                

                for(grid_col_idx = 0; grid_col_idx < grid_width; grid_col_idx++){

                    // check column bounds
                    int global_col = grid_width*j + grid_col_idx;
                    if(global_col >= m){
                        break;
                    }
                        
                    // check if we have a non-zero value
                    int index = global_row*m + global_col;
                    
                    if(matrix[index] != 0){
                        local_A_len++;
                        local_colidx_len++;
                    }

                }
                
            }

            // write final amt
            local_rowptr_len++;

            // Update max values
            if(local_A_len > max_A_len)
                max_A_len = local_A_len;

            if(local_rowptr_len > max_rowptr_len)
                max_rowptr_len = local_rowptr_len;

            if(local_colidx_len > max_colidx_len)
                max_colidx_len = local_colidx_len;
        }
    }

    *A_len = max_A_len;
    *A_rowptr_len = max_rowptr_len;
    *A_colidx_len = max_colidx_len;
}

/**
 * Retrieves relevant parameters for the memory calculation of the COO formatted matrix
 * @param matrix double matrix
 * @param n row dimension of matrix
 * @param m column dimension of matrix 
 * @param Px grid dimension column
 * @param Py grid dimension row
 * @param A_len Largest A_len of any submatrix 
 */
void retrieve_grid_coo_grid_params(double* matrix, int n, int m, int Px, int Py, int* A_len){

    int grid_col_idx;
    int grid_row_idx;

    // If grid dimension do not align, extend by one
    int grid_height = n % Py == 0 ? n / Py : n/Py + 1;
    int grid_width = m % Px == 0 ? m / Px : m/Px + 1;

    int max = 0;
    int local = 0;

    // Traverse gridwise (from left to right) and find largest A_len of any submatrix 
    for(int i=0; i<Py; i++){
        for(int j=0; j<Px; j++){

            local = 0;

            // Here, we traverse inside the grid
            for(grid_row_idx = 0; grid_row_idx < grid_height; grid_row_idx++){
                
                // check row bounds
                int global_row = grid_height*i + grid_row_idx;
                if(global_row >= n){
                    break;
                }
                
                for(grid_col_idx = 0; grid_col_idx < grid_width; grid_col_idx++){

                    // check column bounds
                    int global_col = grid_width*j + grid_col_idx;
                    if(global_col >= m){
                        break;
                    }
                        
                    // check if we have a non-zero value
                    int index = global_row*m + global_col;
                    
                    if(matrix[index] != 0){
                        local++;
                    }

                }
                
            }

            // Check and update if submatrix has higher A_len 
            if(local > max){
                max = local;
            }
        }
    }

    // Write variables back
    *A_len = max;
}

/**
 * Retrieves relevant parameters for the memory calculation of the ELLPACK formatted matrix
 * Note: Here we are only interested in A_len, i.e. the line length in our final output.
 * @param matrix double matrix
 * @param n row dimension of matrix
 * @param m column dimension of matrix 
 * @param Px grid dimension column
 * @param Py grid dimension row
 * @param A_len Largest A_len of any submatrix 
 */
void retrieve_to_grid_ellpack_grid_params(double* matrix, int n, int m, int Px, int Py, int* A_len){

    int grid_col_idx;
    int grid_row_idx;

    // If grid dimension do not align, extend by one
    int grid_height = n % Py == 0 ? n / Py : n/Py + 1;
    int grid_width = m % Px == 0 ? m / Px : m/Px + 1;

    int max = 0;
    int local = 0;

    // Traverse gridwise (from left to right)
    for(int i=0; i<Py; i++){
        for(int j=0; j<Px; j++){

            // Here, we traverse inside the grid
            for(grid_row_idx = 0; grid_row_idx < grid_height; grid_row_idx++){
                
                // check row bounds
                int global_row = grid_height*i + grid_row_idx;
                if(global_row >= n){
                    break;
                }

                local = 0;

                for(grid_col_idx = 0; grid_col_idx < grid_width; grid_col_idx++){

                    // check column bounds
                    int global_col = grid_width*j + grid_col_idx;
                    if(global_col >= m){
                        break;
                    }
                        
                    // check if we have a non-zero value
                    int index = global_row*m + global_col;
                    
                    if(matrix[index] != 0){
                        local++;
                    }

                }

                // Check and update if submatrix has higher A_len 
                if(local > max){
                    max = local;
                }
            }
        }
    }

    // Write variables back
    *A_len = max;
}

/**
 * Checks if a file with a requested filename is available
 * @param filename A string containing the filename
 */
bool isFileAvailable(const char* filename) {
    FILE* file = fopen(filename, "r");
    if (file) {
        fclose(file);
        return true;
    }
    return false;
}


int main(int argc, char **argv)
{   
    double* m;
    double* gen;

    int height = atoi(argv[1]);
    int width = atoi(argv[2]);
    int density = atoi(argv[3]);

    // Check if file is available and if not generate.
    char filename[100];
    sprintf(filename, "mat_%d_%d_%d.txt", height, width, density);

    if (isFileAvailable(filename)) {
        gen = read_csv_matrix(filename, height, width); 
    } else {
        // Generate matrix (Density in percent)
        gen = generate_sparse_matrix(density, height, width); 
        write_csv_matrix(gen, height, width, filename);
    }

    int grid_height = atoi(argv[4]);
    int grid_width = atoi(argv[5]);

    // Format types
    // 0: CSC
    // 1: CSR
    // 2: Custom
    // 3: Ellpack
    int type = atoi(argv[6]);

    // Declare variables for usage
    int A_val_len, A_rowidx_len, A_colptr_len, A_len, A_colidx_len, A_rowptr_len;

    switch(type){
        case 0:
            // Retrieve grid CSC
            retrieve_grid_csc_grid_params(gen, height, width, grid_width, grid_height, &A_val_len, &A_rowidx_len, &A_colptr_len);
            printf("%d\n%d\n%d\n", A_val_len, A_rowidx_len, A_colptr_len);
            break;
        case 1:
            // Retrieve grid CSR
            retrieve_to_grid_csr_grid_params(gen, height, width, grid_width, grid_height, &A_val_len, &A_colidx_len, &A_rowptr_len);
            printf("%d\n%d\n%d\n", A_val_len, A_colidx_len, A_rowptr_len);
            break;
        case 2:
            // Retrieve grid Custom
            retrieve_grid_coo_grid_params(gen, height, width, grid_width, grid_height, &A_len);
            printf("%d\n", A_len);
            break;
        case 3:
            // Retrieve grid Ellpack
            retrieve_to_grid_ellpack_grid_params(gen, height, width, grid_width, grid_height, &A_len);
            printf("%d\n", A_len);
            break;
        default:
            printf("Enter a correct format type. 0: CSC, 1: CSR, 2: Custom, 3: Ellpack");
    }

    return 0;
 }