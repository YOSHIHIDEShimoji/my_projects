#!/bin/bash
set -e

echo
echo "----- [03] Start generating SSH key -----"
echo

SSH_DIR="$HOME/.ssh"
SSH_KEY="$SSH_DIR/id_ed25519"

# .sshディレクトリがなければ作成
if [ ! -d "$SSH_DIR" ]; then
  echo "Creating .ssh directory..."
  mkdir -p "$SSH_DIR"
  chmod 700 "$SSH_DIR"
fi

# SSHキーがすでにあるかチェック
if [ -f "$SSH_KEY" ]; then
  echo "SSH key already exists: $SSH_KEY"
else
  echo "No SSH key found. Generating a new SSH key..."

  # Gitのuser.emailを取得
  email=$(git config --global user.email)

  if [ -z "$email" ]; then
    # Git設定にemailがない場合はユーザーに聞く
    read -rp "Enter your email for the SSH key: " email
  else
    echo "Using Git configured email: $email"
  fi

  # SSHキー作成（パスフレーズなし）
  ssh-keygen -t ed25519 -C "$email" -f "$SSH_KEY" -N ""

  echo "New SSH key has been generated: $SSH_KEY"
fi

# ssh-agent起動してキーを登録
echo "Starting ssh-agent and adding the key..."
eval "$(ssh-agent -s)"
ssh-add "$SSH_KEY"

# 公開鍵の場所を案内
echo "Public key location: ${SSH_KEY}.pub"

