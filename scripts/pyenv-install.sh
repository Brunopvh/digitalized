#!/bin/bash
#
#
# Usage: curl https://pyenv.run | bash
#
# For more info, visit: https://github.com/pyenv/pyenv-installer
#
# pyenv install 3.13:latest
# pyenv global 3.13.1  # (ou a versão exata instalada)
# python --version     # Deve retornar 3.13
# 

THIS_FILE=$(readlink -f "$0")
THIS_DIR=$(dirname "$THIS_FILE")
LIB_VENV="${THIS_DIR}/lib_venv.sh"
source "$LIB_VENV" || exit 1
source "$FILE_VENV" || exit 1
	

function install_req(){
	sudo apt update
	sudo apt install build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev 
	sudo apt install wget libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
}

function install_py_env(){
	#curl https://pyenv.run | bash
	#local tmp_file_run=~/Downloads/pyenv-installer.sh
	local tmp_file_run="$(mktemp).sh"
	local url_pyenv='https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer'
	
	wget "$url_pyenv" -O "${tmp_file_run}"
	chmod +x "${tmp_file_run}"
	bash "${tmp_file_run}"
}

function add_pyenv_path(){
	local PYENV_DIR="$HOME/.pyenv/bin"

	# Incluir diretório pyenv no PATH
	if ! grep "${PYENV_DIR}" ~/.bashrc; then
		echo -e "Configurando PATH em ~/.bashrc"
		echo -e "PATH=${PYENV_DIR}:$PATH" >> ~/.bashrc
	fi

	# Iniciar pyenv em cada login
	if ! grep "eval.*pyenv init --path)" ~/.bashrc; then
			echo -e "Configurando pyenv init em ~/.bashrc"
			echo -e "eval \"\$(pyenv init --path)\"" >> ~/.bashrc
			echo -e "eval \"\$(pyenv virtualenv-init -)\"" >> ~/.bashrc
	fi
	#echo -e $PATH | grep -q "${PYENV_DIR}" || export PATH=$PATH:"${PYENV_DIR}"
}

function main() {
  install_req
  install_py_env
  add_pyenv_path
}

main "$@"
