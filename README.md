# **Efficient Sparse Matrix Multiplication on the Cerebras WSE-2**  

This repository accompanies the paper [**"Sparse Matrix Multiplication on Cerebras WSE-2: Evaluating SpMM Algorithms in Spatial Computing"**](https://filipdob.ro/papers/ProjectCerebras.pdf), where we explores efficient **sparse matrix multiplication (SpMM)** algorithms on the **Cerebras WSE-2**, a cutting-edge **spatial accelerator** with massive parallelization capabilities. 

## **Abstract**  
Sparse matrix multiplications are a fundamental component of various scientific disciplines, including **computational physics, machine learning, and data analysis**. Efficient and scalable algorithms for sparse matrix multiplications are essential for improving the performance of crucial computational methods and applications.  

This work investigates the performance of sparse matrix multiplications on a novel platform, the **Cerebras WSE-2**. The **spatial architecture** of the WSE-2 enables **unprecedented levels of parallelism**, surpassing previous studies in the field. Our research involves implementing four sparse matrix multiplication algorithms, each utilizing different **sparse storage formats**. We optimize these implementations for overall performance on the WSE-2 and conduct **performance analysis** to isolate and examine computational efficiency.  

Our findings indicate that optimizing sparse matrix multiplication for overall performance on the **WSE-2** may lead to **computation task performance degradation**, particularly at **higher sparsity levels**. This highlights the trade-off between **global performance optimization and computational efficiency**, offering valuable insights for future **hardware-aware** SpMM optimizations on the Cerebras WSE-2.  

---

## **Resources & References**  
Here are key references and learning materials related to the project:  

- 🎥 [**Cerebras Hardware Video Playlist**](https://www.youtube.com/playlist?list=PLCiO1ulV2l-buO1QruG7bGkmREvhXDckc)  
- 🚀 [**Computational Fluid Dynamics Acceleration with Cerebras**](https://www.youtube.com/watch?v=AZEoSkbPsZI)  
- 🖥️ [**Cerebras SDK Overview Video**](https://www.youtube.com/watch?v=ZXJzS_LHxcQ)  
- 📄 [**Technical Overview of the Cerebras SDK (PDF)**](https://f.hubspotusercontent30.net/hubfs/8968533/Cerebras%20SDK%20Technical%20Overview%20White%20Paper.pdf)  
- 📜 [**Graph Neural Networks (GNN) Paper**](https://arxiv.org/abs/2205.09702)  

---

## **Repository Structure**  
The repository is organized as follows:  

📂 **`summaries/`** – Summaries of reviewed material  
📂 **`documents/`** – Research papers and other relevant PDFs  
📂 **`src/`** – Source code for various implementations  
📂 **`src/benchmarks/`** – Benchmarking-related source code  
📂 **`test/`** – Input and output files for testing  
📂 **`lib/`** – External libraries used in the project  
📂 **`plots/`** – Final plots and figures from benchmarking  

---

## **Sparse Matrix Format Conversion**  

### **`convertor.c` – Generating Sparse Matrices**  
To generate a **random sparse matrix** with specified dimensions and density, run:  

```sh
./a.out A_height A_width A_density Py Px Format
```

| Parameter | Description |
|-----------|------------|
| `A_height` | Number of rows in matrix A (N) |
| `A_width` | Number of columns in matrix A (K) |
| `A_density` | Matrix density (as a percentage) |
| `Py` | Number of processing element (PE) rows |
| `Px` | Number of processing element (PE) columns |
| `Format` | 0: CSC, 1: CSR, 2: Custom |

This command generates **four output files** prefixed with `tmp`.  

### **`add_padding.py` – Adding Padding to Converted Files**  
To add **padding** to the converted files (prefix `tmp`), run:  

```sh
python3 add_padding.py Format
```

| Parameter | Description |
|-----------|------------|
| `Format` | 0: CSC, 1: CSR, 2: Custom |

The script appends **`_pad`** to the new padded files by default.  

---

## **Simulation Workflow**  
To execute a simulation on the WSE-2:  

1. **Generate a sparse matrix** and corresponding input files using:  
   ```sh
   src/sparse_format_convertors/convertor.c
   ```  
2. **Add padding** to the generated files:  
   ```sh
   src/sparse_format_convertors/add_padding.py
   ```  
3. **Move the input files** to the simulator's `test_vectors/` folder.  
4. **Modify `commands.sh`** to configure the new input files, including:  
   - `Nt`, `Kt`, `M`  
   - Array lengths  
   - Prefix name (`A_prefix`) for input files (`col_ptr`, `row_ptr`, `val`)  
5. **Run the simulation** with the adjusted parameters.  

---

## **Automated Testing**  
For automated validation of implementations, run:  

```sh
src/automated_testing/full_test.sh
```

**⚠️ Prerequisite:** Before executing `full_test.sh`, compile `convertor.c` using **GCC** in `src/sparse_format_convertors/`.  

---

## **Contributing**  
Contributions are welcome! If you have improvements or bug fixes, feel free to:  

- Submit a **pull request**  
- Report issues via **GitHub Issues**  

For major changes, consider opening a discussion first.  

---
 
