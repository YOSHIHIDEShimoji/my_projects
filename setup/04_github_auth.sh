#!/bin/bash
set -e

echo
echo "----- [04] Start GitHub authentication -----"
echo

# ghコマンドがインストールされているか確認
if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is not installed."
  echo "Please install gh before running this script."
  exit 1
fi

# すでに認証済みか確認
if gh auth status >/dev/null 2>&1; then
  echo "Already authenticated with GitHub."
else
  echo "Not authenticated with GitHub. Starting authentication..."
  gh auth login
fi

