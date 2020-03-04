#!/bin/bash

set -eu

CURRENT_DIR=$(pwd)
SCRIPT_DIR=$(dirname $0)
DATA_DIR="../output_sample"
OUTPUT_DIR="./consumption_by_version"
cd ${SCRIPT_DIR}

VERSION=$(grep "Istio:" $DATA_DIR/report.md | sed "s/- Istio: //g")

TARGET="table_istioproxy_*"

for i in $(find $DATA_DIR -name ${TARGET}); do
    VALUE=$(grep 1000, $i | sed "s/1000,//g")
    FILE=$(basename $i)
    
    set +e
    grep "${VERSION}" "${OUTPUT_DIR}/${FILE}" > /dev/null
    RETURN=$?
    set -e
    
    if [ $RETURN = 0 ]; then
        echo "Skip: istio-${VERSION} is already exist in ${OUTPUT_DIR}/${FILE}"
    else
        echo "${VERSION},${VALUE}" >> ${OUTPUT_DIR}/${FILE}
    fi
done

TARGET="table_controlplane_*"

for i in $(find $DATA_DIR -name ${TARGET}); do
    VALUE=$(grep 1000, $i | sed "s/1000,//g")
    FILE=$(basename $i)
    
    COL_NAME=$(head -2 $i | sed -e "s/^/${VERSION},/g")
    
    if [ ! -f "${OUTPUT_DIR}/${FILE}" ]; then
        touch "${OUTPUT_DIR}/${FILE}"
    fi
    
    set +e
    grep "${VERSION}" "${OUTPUT_DIR}/${FILE}" > /dev/null
    RETURN=$?
    set -e
    
    if [ $RETURN = 0 ]; then
        echo "Skip: istio-${VERSION} is already exist in ${OUTPUT_DIR}/${FILE}"
    else
        echo "${COL_NAME}" >> "${OUTPUT_DIR}/${FILE}"
        echo "${VERSION},${VALUE}" >> "${OUTPUT_DIR}/${FILE}"
    fi
done

cd ${CURRENT_DIR}