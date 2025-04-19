#!/bin/bash
set -e

echo
echo "----- [06] Start cloning dotfiles repository -----"
echo

# クローン先ディレクトリ（名前をdotfiles_cloneに変更）
TARGET_DIR="$HOME/dotfiles_clone"

# デフォルトのリポジトリURL
DEFAULT_REPO_URL="git@github.com:YOSHIHIDEShimoji/dotfiles.git"

# クローン先がすでに存在するかチェック
if [ -d "$TARGET_DIR" ]; then
  echo "Directory already exists: $TARGET_DIR"
  echo "Skipping cloning dotfiles."
  exit 0
fi

# リポジトリURLの確認
echo "Default repository URL is: $DEFAULT_REPO_URL"
read -rp "Use this repository? (y/n): " answer

if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
  REPO_URL="$DEFAULT_REPO_URL"
else
  read -rp "Enter your dotfiles GitHub repository URL (SSH or HTTPS): " REPO_URL
fi

# dotfilesリポジトリをクローン
echo "Cloning dotfiles repository into $TARGET_DIR..."
git clone "$REPO_URL" "$TARGET_DIR"

echo "Dotfiles repository has been cloned."

