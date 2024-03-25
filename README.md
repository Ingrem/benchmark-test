# Benchmark-test

This repository contains suites for benchmark testing of zkLLVM toolchain

### Dependencies

Python >= 3.7

### Prerequisites

Build the toolchain on local machine :

1. Build the assigner https://github.com/nilFoundation/zkllvm
    
    You will need to build the assigner following the guide in the zkllvm repo.
    
2. Install the [proof-generator](https://github.com/NilFoundation/proof-producer)
    
    Proof generator will be needed to produce the proof
    
3. Clone [zkllvm-template](https://github.com/NilFoundation/zkllvm-template) and install dependencies from readme
    
    We will need this repo to compile experiments
    
4. Install the valgrind and massif-visualizer
    
    ```
    sudo apt-get install valgrind massif-visualizer
    ```

### Benchmarking example

This example can be used to first benchmark test. 

Open the zkllvm-tepmlate repo and change the content of your src/main.cpp to this code:

```cpp
#include <nil/crypto3/hash/algorithm/hash.hpp>
#include <nil/crypto3/hash/sha2.hpp>

using namespace nil::crypto3;

bool is_same(size_t a, size_t b)
{
    return a == b;
}

[[circuit]] bool validate_number(
    [[private_input]] size_t a)
{
    return is_same(a, 5);
}
```

Then change src/main-input.json:

```cpp
[
    {
        "int": 5
    }
]
```

### Benchmark scripts using

Need to specify the path to the root directory of zkllvm-template and call script with python

```
python3 test_suites/benchmark-test.py /path/to/zkllvm/template
```

### Results

This test suites output results to the console. 

Memory - memory in peak, collected with valgrind.

Time - collected with "time" utility without valgrind overhead