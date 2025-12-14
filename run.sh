#!/bin/bash

THIS_SCRIPT=$(readlink -f "$0")
DIR_PROJECT=$(dirname "$THIS_SCRIPT")
FILE_MAIN="${DIR_PROJECT}/tests.py"

LIB_VENV="${DIR_PROJECT}/scripts/lib_venv.sh"
source "${LIB_VENV}" || exit 1
echo -e "Ativando VEVN em: $FILE_VENV"
source "${FILE_VENV}" || exit 1

function main(){
    clear
    python3 "$FILE_MAIN"
}

main "$@"
