#!/bin/bash

# Test cases
TEST_CASES=(
    "-g FN42aa"
    "-g JJ00"
    "-l 42.65148,-71.32457 -p 3"
    "-l 0,0 -p 2"
)

# Function to run tests
run_tests() {
    local cmd=$1
    echo "Testing $cmd"
    for test_case in "${TEST_CASES[@]}"; do
        echo "Running: $cmd $test_case"
        eval "$cmd $test_case"
        echo
    done
}

# Compile C program
cd /workspace/maidenhead
make

# Run tests for C
run_tests "./maidenhead"

# Run tests for Python
run_tests "python3 maidenhead_new.py"

# Run tests for JavaScript
run_tests "node cli.js"