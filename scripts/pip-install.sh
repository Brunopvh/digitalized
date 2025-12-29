#!/bin/bash

THIS_FILE=$(readlink -f "$0")
THIS_DIR=$(dirname "$THIS_FILE")
LIB_VENV="${THIS_DIR}/lib_venv.sh"
source "$LIB_VENV" || exit 1
source "$FILE_VENV" || exit 1

function _python_cmd(){
  python3 "$@"
}

function main() {
  echo -e " $(_python_cmd -V) ... $(command -v python3)\n"
  _python_cmd -m pip "$@"
}

main "$@"
