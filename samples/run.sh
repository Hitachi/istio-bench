#!/bin/bash

#
# Run istio-bench to generate
# sample results in `output_sample` directory
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

python ./istio-bench.py \
--max_pod 400 \
--interval 50 \
--output $OUT_DIR \
--verbose=0

cd ${CURRENT_DIR}
