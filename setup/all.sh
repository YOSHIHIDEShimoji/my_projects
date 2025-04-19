#!/bin/bash
set -e

# スクリプトのあるディレクトリに移動
cd "$(dirname "$0")"

# 順番にスクリプトを実行
bash 01_install_apps.sh
bash 02_setup_gitconfig.sh
bash 03_generate_ssh_key.sh
bash 04_github_auth.sh
bash 05_upload_ssh_key.sh
bash 06_clone_dotfiles.sh
bash 07_run_dotfiles_clone_install.sh

echo "All setup scripts have been successfully executed."

