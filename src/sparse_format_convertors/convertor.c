#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h> 

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

    // Initialize a matrix with all elements as 0.0 
    double* matrix = (double*) calloc(n * m, sizeof(double)); 
  
    // Generate random numbers in range [0,1] 
    srand(time(NULL)); 
  
    // Fill the matrix with random numbers 
    // with a given density 
    for (int i=0; i<n; i++) 
    { 
        for (int j=0; j<m; j++) 
        { 
            if (rand()%100 < density){ 
                matrix[i*m + j] = (double)(rand()%10 + 1); 
            }
        } 
    } 
  
    // Return the matrix 
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
 * Converts a matrix containing doubles to local csc grid format and writes it into three files in row-wise grid traversal.
 * Each line for the file encodes the CSC format specifier for the grid (going from left to right).
 * If a grid is empty, it will print an empty line in 'filename_val' and 'filename_row_idx' and it will print '0,0' in 'filename_col_ptr'. 
 * @param mat double matrix
 * @param n row dimension of matrix 
 * @param m column dimension of matrix 
 * @param Px grid dimension column
 * @param Py grid dimension row
 * @param filename_val filename to write the CSC values array into
 * @param filename_row_idx filename to write the CSC row index array into
 * @param filename_col_ptr filename to write the CSC column pointer array into
 */
void convert_to_grid_csc_grid(double* matrix, int n, int m, int Px, int Py, char* filename_val, char* filename_row_idx, char* filename_col_ptr){
    // open files
    FILE* fp_val;
    fp_val = fopen(filename_val, "w");
    if (fp_val == NULL) {
        printf("Error opening file!\n");
        exit(1);
    }

    FILE* fp_row_idx;
    fp_row_idx = fopen(filename_row_idx, "w");
    if (fp_row_idx == NULL) {
        printf("Error opening file!\n");
        exit(1);
    }

    FILE* fp_col_ptr;
    fp_col_ptr = fopen(filename_col_ptr, "w");
    if (fp_col_ptr == NULL) {
        printf("Error opening file!\n");
        exit(1);
    }

    int grid_col_idx;
    int grid_row_idx;


    // If grid dimension do not align, extend by one
    int grid_height = n % Py == 0 ? n / Py : n/Py + 1;
    int grid_width = m % Px == 0 ? m / Px : m/Px + 1;

    // Traverse gridwise (from left to right)
    for(int i=0; i<Py; i++){
        for(int j=0; j<Px; j++){


            // Here, we traverse inside the grid
            int num_elems = 0;
            for(grid_col_idx = 0; grid_col_idx < grid_width; grid_col_idx++){
                
                // check column bounds
                int global_col = grid_width*j + grid_col_idx;
                if(global_col >= m){
                    break;
                }

                // write column pointer
                fprintf(fp_col_ptr, "%d,", num_elems);
                

                for(grid_row_idx = 0; grid_row_idx < grid_height; grid_row_idx++){
                    
                    // check row bounds
                    int global_row = grid_height*i + grid_row_idx;
                    if(global_row >= n){
                        break;
                    }

                    // check if we have a non-zero value
                    int index = global_row*m + global_col;
                    
                    if(matrix[index] != 0){

                        num_elems++;

                        fprintf(fp_val, "%f,", matrix[index]);
                        fprintf(fp_row_idx, "%d,", grid_row_idx);
                    }

                }
                
            }

            // write final amt
            fprintf(fp_col_ptr, "%d", num_elems);

            fprintf(fp_val, "\n");
            fprintf(fp_row_idx, "\n");
            fprintf(fp_col_ptr, "\n");
        }
    }

    fclose(fp_val);
    fclose(fp_row_idx);
    fclose(fp_col_ptr);
}


/**
 * Converts a matrix containing doubles to local csr grid format and writes it into three files in row-wise grid traversal.
 * Each line for the file encodes the CSR format specifier for the grid (going from left to right).
 * If a grid is empty, it will print an empty line in 'filename_val' and 'filename_col_idx' and it will print '0,0' in 'filename_row_ptr'. 
 * @param mat double matrix
 * @param n row dimension of matrix 
 * @param m column dimension of matrix 
 * @param Px grid dimension column
 * @param Py grid dimension row
 * @param filename_val filename to write the CSR values array into
 * @param filename_col_idx filename to write the CSR col index array into
 * @param filename_row_ptr filename to write the CSR column pointer array into
 */
void convert_to_grid_csr_grid(double* matrix, int n, int m, int Px, int Py, char* filename_val, char* filename_col_idx, char* filename_row_ptr){
    // open files
    FILE* fp_val;
    fp_val = fopen(filename_val, "w");
    if (fp_val == NULL) {
        printf("Error opening file!\n");
        exit(1);
    }

    FILE* fp_col_idx;
    fp_col_idx = fopen(filename_col_idx, "w");
    if (fp_col_idx == NULL) {
        printf("Error opening file!\n");
        exit(1);
    }

    FILE* fp_row_ptr;
    fp_row_ptr = fopen(filename_row_ptr, "w");
    if (fp_row_ptr == NULL) {
        printf("Error opening file!\n");
        exit(1);
    }

    int grid_col_idx;
    int grid_row_idx;


    // If grid dimension do not align, extend by one
    int grid_height = n % Py == 0 ? n / Py : n/Py + 1;
    int grid_width = m % Px == 0 ? m / Px : m/Px + 1;


    // Traverse gridwise (from left to right)
    for(int i=0; i<Py; i++){
        for(int j=0; j<Px; j++){


            // Here, we traverse inside the grid
            int num_elems = 0;
            for(grid_row_idx = 0; grid_row_idx < grid_height; grid_row_idx++){
                
                // check row bounds
                int global_row = grid_height*i + grid_row_idx;
                if(global_row >= n){
                    break;
                }


                // write row pointer
                fprintf(fp_row_ptr, "%d,", num_elems);
                

                for(grid_col_idx = 0; grid_col_idx < grid_width; grid_col_idx++){

                    // check column bounds
                    int global_col = grid_width*j + grid_col_idx;
                    if(global_col >= m){
                        break;
                    }
                        
                    // check if we have a non-zero value
                    int index = global_row*m + global_col;
                    
                    if(matrix[index] != 0){

                        num_elems++;

                        fprintf(fp_val, "%f,", matrix[index]);
                        fprintf(fp_col_idx, "%d,", grid_col_idx);
                    }

                }
                
            }

            // write final amt
            fprintf(fp_row_ptr, "%d", num_elems);

            fprintf(fp_val, "\n");
            fprintf(fp_col_idx, "\n");
            fprintf(fp_row_ptr, "\n");
        }
    }

    fclose(fp_val);
    fclose(fp_col_idx);
    fclose(fp_row_ptr);
}

/**
 * Converts a matrix containing doubles to local custom grid format and writes it into three files in row-wise grid traversal.
 * Each line for the file encodes the custom grid format specifier for the grid (going from left to right).
 * If a grid is empty, it will print an empty line in 'filename_val', 'filename_x' and 'filename_y'. 
 * @param mat double matrix
 * @param n row dimension of matrix
 * @param m column dimension of matrix 
 * @param Px grid dimension column
 * @param Py grid dimension row
 * @param filename_val filename to write the CSR values array into
 * @param filename_x filename to write the custom x index array into
 * @param filename_y filename to write the custom y index array into
 */
void convert_to_grid_custom_grid(double* matrix, int n, int m, int Px, int Py, char* filename_val, char* filename_x, char* filename_y){
    // open files
    FILE* fp_val;
    fp_val = fopen(filename_val, "w");
    if (fp_val == NULL) {
        printf("Error opening file!\n");
        exit(1);
    }

    FILE* fp_x;
    fp_x = fopen(filename_x, "w");
    if (fp_x == NULL) {
        printf("Error opening file!\n");
        exit(1);
    }

    FILE* fp_y;
    fp_y = fopen(filename_y, "w");
    if (fp_y == NULL) {
        printf("Error opening file!\n");
        exit(1);
    }

    int grid_col_idx;
    int grid_row_idx;


    // If grid dimension do not align, extend by one
    int grid_height = n % Py == 0 ? n / Py : n/Py + 1;
    int grid_width = m % Px == 0 ? m / Px : m/Px + 1;


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
                
                for(grid_col_idx = 0; grid_col_idx < grid_width; grid_col_idx++){

                    // check column bounds
                    int global_col = grid_width*j + grid_col_idx;
                    if(global_col >= m){
                        break;
                    }
                        
                    // check if we have a non-zero value
                    int index = global_row*m + global_col;
                    
                    if(matrix[index] != 0){
                        fprintf(fp_y, "%d,", grid_row_idx);
                        fprintf(fp_val, "%f,", matrix[index]);
                        fprintf(fp_x, "%d,", grid_col_idx);
                    }

                }
                
            }

            fprintf(fp_val, "\n");
            fprintf(fp_x, "\n");
            fprintf(fp_y, "\n");
        }
    }

    fclose(fp_val);
    fclose(fp_x);
    fclose(fp_y);
}


int main(int argc, char **argv)
{   
    double* m;
    double* gen;

    printf("A matrix:\n");
    printf("Height: %s\n", argv[1]);
    printf("Width: %s\n", argv[2]);
    printf("Density: %s\n", argv[3]);
    int height = atoi(argv[1]);
    int width = atoi(argv[2]);
    int density = atoi(argv[3]);

    // Generate matrix (Density in percent)
    gen = generate_sparse_matrix(density, height, width); 
    write_csv_matrix(gen, height, width, "tmp.csv");


    printf("=========================\n");
    printf("Grid size:\n");
    printf("Height: %s\n", argv[4]);
    printf("Width: %s\n", argv[5]);
    int grid_height = atoi(argv[4]);
    int grid_width = atoi(argv[5]);

    printf("=========================\n");
    printf("Format type: ");
    // Format types
    // 0: CSC
    // 1: CSR
    // 2: Custom
    int type = atoi(argv[6]);

    switch(type){
        case 0:
            // Convert to grid CSC
            convert_to_grid_csc_grid(gen, height, width, grid_width, grid_height, "tmp_val.csv", "tmp_row_idx.csv", "tmp_col_ptr.csv");
            printf("CSC\n");
            break;
        case 1:
            // Convert to grid CSR
            convert_to_grid_csr_grid(gen, height, width, grid_width, grid_height, "tmp_val.csv", "tmp_col_idx.csv", "tmp_row_ptr.csv");
            printf("CSR\n");
            break;
        case 2:
            // Convert to grid Custom
            convert_to_grid_custom_grid(gen, height, width, grid_width, grid_height, "tmp_val.csv", "tmp_x.csv", "tmp_y.csv");
            printf("Custom\n");
            break;
        default:
            printf("Enter a correct format type. 0: CSC, 1: CSR, 2: Custom");
    }

    return 0;
 }