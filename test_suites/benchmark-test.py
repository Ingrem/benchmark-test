"""
Suite run benchmark test for proof generation and assigner
Can be used with any zkllvm-tepmlate input experiments

Results:
Memory - memory in peak, collected with valgrind.
Time - collected with "time" utility without valgrind overhead
"""

import re
import subprocess
import argparse


def execute_command(command: str):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, executable='/bin/bash')
    output, error = process.communicate()

    if process.returncode != 0:
        print(error)

    return output, error


def get_memory(valgrid_stdout: str):
    file_name = re.search(r'==(\d+)==', valgrid_stdout).group(1)
    peak_snapshot_row, _ = execute_command(f"ms_print massif.out.{file_name} | grep peak")
    peak_snapshot_number = re.search(r'(\d+)\s+\(peak\)', peak_snapshot_row).group(1)
    snapshot_row, _ = execute_command(
        f'ms_print massif.out.{file_name} | grep -E "^\s*{peak_snapshot_number}\s+"')
    max_memory = snapshot_row.split()[1].replace(",", "")
    max_memory_gb = int(max_memory) / (1024 ** 3)
    return max_memory_gb


def get_time(time_stdout):
    real_time = re.search(r'real\t(\d+)m(\d+\.\d+)s', time_stdout)
    total_seconds = int(real_time.group(1)) * 60 + float(real_time.group(2))
    return total_seconds


# getting path to zkllvm-template root dir
parser = argparse.ArgumentParser()
parser.add_argument('file_path', type=str, help='zkllvm-template path')
args = parser.parse_args()
execute_command(f'cd {args.file_path}')

print("Compile the circuit")
execute_command('cmake -G "Unix Makefiles" -B ${ZKLLVM_BUILD:-build} -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER=clang-zkllvm .')
execute_command('make -C ${ZKLLVM_BUILD:-build} template')

print("Measure assigner")
_, assigner_valgrid_err = execute_command(
    'valgrind --tool=massif assigner -b build/src/template.ll -p ./src/main-input.json -c build/src/template.crct -t build/src/template.tbl -e pallas'
)
assigner_max_memory_gb = get_memory(assigner_valgrid_err)

_, assigner_time = execute_command('time assigner -b build/src/template.ll -p ./src/main-input.json -c build/src/template.crct -t build/src/template.tbl -e pallas')
assigner_total_seconds = get_time(assigner_time)

print("Measure proof generation")
_, proof_valgrid_err = execute_command(
    'valgrind --tool=massif proof-generator-single-threaded --circuit  build/src/template.crct --assignment build/src/template.tbl --proof build/proof.bin'
)
proof_max_memory_gb = get_memory(proof_valgrid_err)

_, proof_time = execute_command('time proof-generator-single-threaded --circuit  build/src/template.crct --assignment build/src/template.tbl --proof build/proof.bin')
proof_total_seconds = get_time(proof_time)

print("\n\rreal data:")
print("Assigner")
print(f"memory: {assigner_max_memory_gb} gb")
print(f"time: {assigner_total_seconds}s")
print("Proof")
print(f"memory: {proof_max_memory_gb} gb")
print(f"time: {proof_total_seconds}s")
