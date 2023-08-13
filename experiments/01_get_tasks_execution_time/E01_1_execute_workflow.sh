#!/bin/bash


PROCESSOR="i5_10300H"
POWER_PROFILE="PERFORMANCE"
#POWER_PROFILE="POWER_SAVE"

DATA_DIR="./${PROCESSOR}_${POWER_PROFILE}"



export OMPCLUSTER_SCHEDULER=nheft
clang++ -fopenmp -fopenmp-targets=x86_64-pc-linux-gnu ./../workflow/matmul.cc -o matmul

mkdir $DATA_DIR

for counter in $(seq 1 10); 
do 
    echo "Execution: $counter";
    export OMPCLUSTER_PROFILE="./matmul_${PROCESSOR}_${POWER_PROFILE}_$counter"

    mpirun -np 2 ./matmul 5 1
    
    rm "${OMPCLUSTER_PROFILE}_head_process.json"
    mv ./matmul_* $DATA_DIR
done



