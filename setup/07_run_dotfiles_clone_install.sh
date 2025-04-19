#!/bin/bash
set -e

echo
echo "----- [07] Start running install.sh from dotfiles_clone -----"
echo

DOTFILES_DIR="$HOME/dotfiles_clone"
INSTALL_SCRIPT="$DOTFILES_DIR/install.sh"

# dotfiles_cloneディレクトリが存在するか確認
if [ ! -d "$DOTFILES_DIR" ]; then
  echo "Directory not found: $DOTFILES_DIR"
  echo "Please clone the dotfiles repository first."
  exit 1
fi

# install.shが存在するか確認
if [ ! -f "$INSTALL_SCRIPT" ]; then
  echo "install.sh not found in $DOTFILES_DIR"
  echo "Please make sure install.sh exists in the cloned repository."
  exit 1
fi

# install.shを実行
echo "Running install.sh from $DOTFILES_DIR..."
bash "$INSTALL_SCRIPT"

echo "install.sh has been executed."

