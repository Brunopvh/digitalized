#!/bin/bash
#
# Intalar uma VENV loacal em sistemas Linux
#
# Em sistemas Windows você pode instalar os módulos com o seguinte comando:
# python.exe -m pip install -r requirements.txt
# python.exe -m pip install 'https://gitlab.com/bschavesbr/file-utils/-/archive/main/file-utils-main.zip'

THIS_FILE=$(readlink -f "$0")
THIS_DIR=$(dirname "$THIS_FILE")
LIB_VENV="${THIS_DIR}/lib_venv.sh"
FILE_REQ="${THIS_DIR}/requirements.txt"
source "$LIB_VENV" || exit 1


USE_PYTHON='python3'
_PYENV_INTERPRETER=~/.pyenv/versions/3.14.2/bin/python3
if [[ -f "$_PYENV_INTERPRETER"  ]]; then 
	USE_PYTHON="$_PYENV_INTERPRETER"
fi


function print_line(){
	echo -e "======================================="
}

function msg(){
	print_line
	echo -e "$@"
}

function add_venv(){
	msg "Instalando VENV ${VENV_NAME} ... Python $($USE_PYTHON -V) \nDestino ... $DIR_VENV"
	sleep 1
	"${USE_PYTHON}" -m venv "$DIR_VENV"
}

function config_venv(){
	source "$FILE_VENV" || exit 1
	"${USE_PYTHON}" -m pip install --upgrade pip
	[[ -f "$FILE_REQ" ]] && "${USE_PYTHON}" -m pip install -r "$FILE_REQ"
}

function main() {
  add_venv
  config_venv
}

main "$@"
