#!/bin/bash
set -e

echo
echo "----- [01] Start installing required applications -----"
echo

# パッケージアップデート
sudo apt update

# 必要なアプリ一覧
PACKAGES=(
  git
  curl
  vim
  gh
  tree
)

# 必須アプリのインストール
for pkg in "${PACKAGES[@]}"; do
  if ! dpkg -l | grep -q "^ii  $pkg"; then
    echo "Installing ${pkg}..."
    sudo apt install -y "${pkg}"
  else
    echo "${pkg} is already installed."
  fi
done

# VS Codeのインストール
if ! command -v code >/dev/null 2>&1; then
  echo "Installing VS Code..."
  
  if [ ! -f /etc/apt/sources.list.d/vscode.list ]; then
    echo "Adding VS Code repository..."
    curl -sSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/microsoft.gpg
    echo "deb [arch=amd64] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list
    sudo apt update
  fi

  sudo apt install -y code
else
  echo "VS Code is already installed."
fi

echo "All required applications have been installed."
