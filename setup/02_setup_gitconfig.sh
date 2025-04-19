#!/bin/bash
set -e

echo
echo "----- [02] Start setting up Git configuration -----"
echo

# すでに.gitconfigがあるか確認
if [ -f "$HOME/.gitconfig" ]; then
  echo "Current Git global configuration:"
  git config --global --list
  echo
  read -rp "Do you want to change the Git global configuration? (y/n): " answer

  if [[ "$answer" != "y" && "$answer" != "Y" ]]; then
    echo "Keeping existing Git configuration."
    exit 0
  fi
fi

# ユーザー名の入力
read -rp "Enter your Git user.name: " username

# メールアドレスの入力
read -rp "Enter your Git user.email: " email

# git configに設定
git config --global user.name "$username"
git config --global user.email "$email"

# 設定確認
echo "Git global configuration has been updated:"
git config --global --list

