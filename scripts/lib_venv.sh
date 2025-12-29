#!/bin/bash

VENV_NAME='user_venv'
PREFIX=~/"var/venv"
if [[ -d '/mnt/dados' ]]; then
  PREFIX='/mnt/dados/var/venv'
fi
mkdir -p "${PREFIX}"
DIR_VENV="${PREFIX}/${VENV_NAME}"
FILE_VENV="$DIR_VENV/bin/activate"

