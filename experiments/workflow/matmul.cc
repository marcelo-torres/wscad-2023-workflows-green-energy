
#include <cassert>
#include <cstdlib>
#include <ctime>
#include <iostream>
#include <memory>
#include <vector>
#include <string>
#include <unistd.h>

#include <omp.h>

class BlockMatrix {
private:
  const int rowsPerBlock;
  const int colsPerBlock;
  const long nRows;
  const long nCols;
  const int nBlocksPerRow;
  const int nBlocksPerCol;
  std::vector<std::vector<std::unique_ptr<long[]>>> Blocks;

public:
  BlockMatrix(const int _rowsPerBlock, const int _colsPerBlock,
              const long _nRows, const long _nCols)
      : rowsPerBlock(_rowsPerBlock), colsPerBlock(_colsPerBlock), nRows(_nRows),
        nCols(_nCols), nBlocksPerRow(_nRows / _rowsPerBlock),
        nBlocksPerCol(_nCols / _colsPerBlock), Blocks(nBlocksPerCol) {
    for (int i = 0; i < nBlocksPerCol; i++) {
      for (int j = 0; j < nBlocksPerRow; j++) {
        Blocks[i].emplace_back(new long[_rowsPerBlock * _colsPerBlock]);
      }
    }
  };

  // Initialize the BlockMatrix from 2D arrays
  void Initialize(const std::vector<long> &matrix) {
    for (int i = 0; i < nBlocksPerCol; i++)
      for (int j = 0; j < nBlocksPerRow; j++) {
        long *CurrBlock = GetBlock(i, j);
        for (int ii = 0; ii < colsPerBlock; ++ii)
          for (int jj = 0; jj < rowsPerBlock; ++jj) {
            int curri = i * colsPerBlock + ii;
            int currj = j * rowsPerBlock + jj;
            CurrBlock[ii + jj * colsPerBlock] = matrix[curri + currj * nCols];
          }
      }
  }

  long Compare(const std::vector<long> &matrix) const {
    long fail = 0;
    for (int i = 0; i < nBlocksPerCol; i++)
      for (int j = 0; j < nBlocksPerRow; j++) {
        long *CurrBlock = GetBlock(i, j);
        for (int ii = 0; ii < colsPerBlock; ++ii)
          for (int jj = 0; jj < rowsPerBlock; ++jj) {
            int curri = i * colsPerBlock + ii;
            int currj = j * rowsPerBlock + jj;

            long m_value = matrix[curri + currj * nCols];
            long bm_value = CurrBlock[ii + jj * colsPerBlock];
            if (bm_value != m_value) {
              fail++;
            }
          }
      }

    // Print results
    printf("Non-Matching Block Outputs: %ld\n", fail);
    return fail;
  }

  long *GetBlock(int i, int j) const {
    assert(i < nBlocksPerCol && j < nBlocksPerRow && "Accessing outside block");
    return Blocks[i][j].get();
  }

  // Print BlockMatrix
  void Print() {
    for (int i = 0; i < nBlocksPerCol; i++)
      for (int j = 0; j < nBlocksPerRow; j++) {
        long *CurrBlock = GetBlock(i, j);
        printf("Block (%d, %d)\n", i, j);
        for (int ii = 0; ii < colsPerBlock; ++ii) {
          for (int jj = 0; jj < rowsPerBlock; ++jj) {
            printf(" %5ld", CurrBlock[ii * colsPerBlock + jj]);
          }
          printf("\n");
        }
        printf("\n");
      }
  }
};

static size_t BS = 0;
static size_t N = 0;

void BlockMatMul_TargetNowait(BlockMatrix &A, BlockMatrix &B, BlockMatrix &C) {
#pragma omp parallel
#pragma omp master
  for (int i = 0; i < N / BS; ++i)
    
    for (int j = 0; j < N / BS; ++j) {
      long *BlockC = C.GetBlock(i, j);
      for (int k = 0; k < N / BS; ++k) {
        long *BlockA = A.GetBlock(k, j);
        long *BlockB = B.GetBlock(i, k);
        #pragma omp target depend(in: BlockA[0], BlockB[0]) \
                           depend(inout: BlockC[0]) \
                           map(to: BlockA[:BS*BS], BlockB[:BS*BS]) \
                           map(tofrom: BlockC[:BS*BS]) nowait
        {
          printf("[WORKER][PID=%d] %d x %d x %d\n", getpid(), i, j, k);

          for(int s = 0; s < 10000000; s++) {

          }

          #pragma omp parallel for
          for (int ii = 0; ii < BS; ++ii)
            for (int jj = 0; jj < BS; ++jj) {
              long sum = 0.0;
              for (int kk = 0; kk < BS; ++kk)
                sum += BlockA[ii * BS + kk] * BlockB[kk * BS + jj];
              BlockC[ii * BS + jj] += sum;
            }
        }
        
      }
    }
}

void Matmul(const std::vector<long> &a, const std::vector<long> &b,
            std::vector<long> &c) {
#pragma omp parallel for
  for (int i = 0; i < N; ++i) {
    for (int j = 0; j < N; ++j) {
      long sum = 0.0;
      for (int k = 0; k < N; ++k) {
        sum += a[i * N + k] * b[k * N + j];
      }
      c[i * N + j] = sum;
    }
  }
}

// Output matrix to stdout
void print_matrix(const std::vector<long> &c, unsigned size) {
  for (int i = 0; i < size; i++) {
    for (int j = 0; j < size; j++) {
      printf(" %5ld", c[i * size + j]);
    }
    printf("\n");
  }
}

int main(int argc, char *argv[]) {
  double t;

  if (argc < 2) {
    fprintf(stderr, "Error: Missing command-line parameters");
    fprintf(stderr, "Usage: %s <MATRIX-SIZE> <BLOCK-SIZE>\n", argv[0]);
    return 1;
  }

  N = std::stoi(argv[1]);
  BS = std::stoi(argv[2]);

  if (N <= 0) {
    fprintf(stderr, "Error: Invalid matrix size '%lu'\n", N);
    return 1;
  }

  if (N % BS != 0) {
    fprintf(stderr, "Error: Invalid block size '%lu'. Must divide N.\n", N);
    return 1;
  }

  std::vector<long> a(N * N);
  std::vector<long> b(N * N);
  std::vector<long> c(N * N, 0.0);

  auto BlockedA = BlockMatrix(BS, BS, N, N);
  auto BlockedB = BlockMatrix(BS, BS, N, N);
  auto BlockedC = BlockMatrix(BS, BS, N, N);

  std::srand((unsigned int)std::time(nullptr));
  for (int i = 0; i < N; ++i) {
    for (int j = 0; j < N; ++j) {
      a[i * N + j] = rand() % 10;
      b[i * N + j] = rand() % 10;
    }
  }

  BlockedA.Initialize(a);
  BlockedB.Initialize(b);
  BlockedC.Initialize(c);

  fprintf(stdout, "<< Matrix Multiplication >>\n");

  t = omp_get_wtime();
  Matmul(a, b, c);
  t = omp_get_wtime() - t;
  fprintf(stdout, "Local MatMul Computation done in %0.6lfs\n", t);

  t = omp_get_wtime();
  BlockMatMul_TargetNowait(BlockedA, BlockedB, BlockedC);
  t = omp_get_wtime() - t;
  fprintf(stdout, "Offloaded BlockMatMul Computation done in %0.6lfs\n", t);

  if (BlockedC.Compare(c) > 0) {
    // exit code to error if there is any missmatch
    return 1;
  }

  return 0;
}
