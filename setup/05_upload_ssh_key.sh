#!/bin/bash
set -e

echo
echo "----- [05] Start uploading SSH public key to GitHub -----"
echo

SSH_PUB_KEY="$HOME/.ssh/id_ed25519.pub"

# 公開鍵ファイルが存在するかチェック
if [ ! -f "$SSH_PUB_KEY" ]; then
  echo "Public SSH key not found: $SSH_PUB_KEY"
  echo "Please generate an SSH key first."
  exit 1
fi

# ghコマンドがインストールされているか確認
if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is not installed."
  echo "Please install gh before running this script."
  exit 1
fi

# ユーザーにタイトルを入力してもらう
read -rp "Enter a title for your SSH key: " TITLE

# SSHキーをGitHubにアップロード
echo "Uploading SSH public key to GitHub with title: $TITLE"
gh ssh-key add "$SSH_PUB_KEY" --title "$TITLE"

echo "SSH public key has been uploaded to GitHub."

