#!/bin/bash

#
# Run istio-bench to generate `output_sample`
#

set -eu

CURRENT_DIR=$(pwd)
SCRIPT_DIR=$(dirname $0)
ISTIO_BENCH_HOMEDIR=$(dirname ${SCRIPT_DIR})

cd ${ISTIO_BENCH_HOMEDIR}

OUT_DIR="./output_sample"
if [ ! -e $OUT_DIR ]; then
    mkdir $OUT_DIR
fi

echo "Run istio-bench"
echo "-------------------"

python ./istio-bench.py 1000\
--by 100 \
--output $OUT_DIR \
--verbose 0

cd ${CURRENT_DIR}
