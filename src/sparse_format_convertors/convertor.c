#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/**
 * Prints matrix elements seperated by '\t' and '\n' to stdout
 * @param matrix pointer to matrix (nxm)
 * @param n row dimension of matrix 
 * @param m column dimension of matrix 
 */
void print_matrix(double *matrix, int n, int m) {
    for (int row=0; row < n; row++) {
        for (int column=0; column < m; column++) {
            printf("%.2f\t", matrix[row * n + column]);
        }
        printf("\n");
    }
}

/**
 * Reads a csv double matrix separated by ',' and returns a C double matrix containing the values
 * @param myFile pointer to file to be read
 * @param n row dimension of matrix 
 * @param m column dimension of matrix 
 */
double* read_csv_matrix(FILE* myFile, int n, int m){
    //  myFile = fopen("test_array.csv","r");

    double* output = malloc(n * m * sizeof(double));

    if (myFile == NULL)
    {
        exit(1);
    }

    // allocate memory
    char *buffer;
    int size = 4096;
    int bytes_read;
    buffer = (char *) malloc (size);
    int idx = 0;
    
    while (1) {
        bytes_read = getline(&buffer, &size, myFile);

        if(bytes_read == -1){
            break;
        }

        const int curr_bytes = bytes_read;
        char buf[curr_bytes];


        // have to copy bytes, because strtok would modify the scaling buffer (=bad)
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
 * Converts a matrix containing doubles to local csc grid format and writes it to a file
 * @param mat double matrix
 * @param n row dimension of matrix 
 * @param m column dimension of matrix 
 * @param Px grid dimension column
 * @param Py grid dimension row
 */
double* convert_to_grid_csc_grid(double* mat, int n, int m, int Px, int Py){

    int grid_col_idx;
    int grid_row_idx;

    int grid_height = n / Py;
    int grid_width = m / Px;

    for(int i=0; i<Py; i++){
        for(int j=0; j<Px; j++){
            for(grid_col_idx = 0; grid_col_idx < grid_width; grid_col_idx++){
                for(grid_row_idx = 0; grid_row_idx < grid_height; grid_row_idx++){
                    // todo
                }
            }
        }
    }

}




int main()
{   
    FILE* myFile;
    myFile = fopen("test_array.csv","r");
    double* m;
    m = read_double_array(myFile, 4,4);

    print_matrix(m, 4, 4);

    return 0;
 }