#!/usr/bin/env python3
"""
PDF Password Remover
自分のPDFファイルのパスワードを解除するためのツール
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional, List
import PyPDF2
from tqdm import tqdm
import pikepdf


class PDFPasswordRemover:
    def __init__(self):
        self.processed_count = 0
        self.failed_count = 0
        
    def remove_password(self, input_path: str, output_path: str, password: str) -> bool:
        """
        PDFファイルからパスワードを解除
        
        Args:
            input_path: 入力PDFファイルのパス
            output_path: 出力PDFファイルのパス
            password: PDFのパスワード
            
        Returns:
            bool: 成功した場合True
        """
        try:
            # pikepdfを使用（より多くのPDF形式に対応）
            with pikepdf.open(input_path, password=password) as pdf:
                pdf.save(output_path)
            return True
        except pikepdf.PasswordError:
            print(f"エラー: パスワードが正しくありません - {input_path}")
            return False
        except Exception as e:
            print(f"エラー: {input_path} の処理中にエラーが発生しました: {str(e)}")
            return False
    
    def try_common_passwords(self, input_path: str, output_path: str, 
                           password_list: Optional[List[str]] = None) -> Optional[str]:
        """
        一般的なパスワードを試す
        
        Args:
            input_path: 入力PDFファイルのパス
            output_path: 出力PDFファイルのパス
            password_list: 試すパスワードのリスト
            
        Returns:
            str: 成功したパスワード、失敗した場合None
        """
        if password_list is None:
            # よく使われるパスワードのリスト
            password_list = [
                "password", "123456", "admin", "1234", "12345",
                "password123", "admin123", "pdf", "pass", "0000",
                "1111", "2222", "9999", "qwerty", "abc123"
            ]
        
        print(f"一般的なパスワードを試しています...")
        for password in tqdm(password_list, desc="パスワード試行"):
            try:
                with pikepdf.open(input_path, password=password) as pdf:
                    pdf.save(output_path)
                    return password
            except pikepdf.PasswordError:
                continue
            except Exception:
                continue
        
        return None
    
    def process_batch(self, input_dir: str, output_dir: str, password: str, 
                     recursive: bool = False) -> None:
        """
        ディレクトリ内のPDFを一括処理
        
        Args:
            input_dir: 入力ディレクトリ
            output_dir: 出力ディレクトリ
            password: PDFのパスワード
            recursive: サブディレクトリも処理するか
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        # 出力ディレクトリを作成
        output_path.mkdir(parents=True, exist_ok=True)
        
        # PDFファイルを検索
        if recursive:
            pdf_files = list(input_path.rglob("*.pdf"))
        else:
            pdf_files = list(input_path.glob("*.pdf"))
        
        if not pdf_files:
            print("PDFファイルが見つかりませんでした。")
            return
        
        print(f"{len(pdf_files)}個のPDFファイルを処理します...")
        
        for pdf_file in tqdm(pdf_files, desc="処理中"):
            # 相対パスを保持して出力
            relative_path = pdf_file.relative_to(input_path)
            output_file = output_path / relative_path
            
            # 出力ディレクトリを作成
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # パスワード解除
            if self.remove_password(str(pdf_file), str(output_file), password):
                self.processed_count += 1
            else:
                self.failed_count += 1
    
    def check_if_encrypted(self, pdf_path: str) -> bool:
        """
        PDFが暗号化されているかチェック
        
        Args:
            pdf_path: PDFファイルのパス
            
        Returns:
            bool: 暗号化されている場合True
        """
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                return reader.is_encrypted
        except Exception:
            # pikepdfでも試す
            try:
                with pikepdf.open(pdf_path) as pdf:
                    return False
            except pikepdf.PasswordError:
                return True
            except Exception:
                return False


def load_password_list(file_path: str) -> List[str]:
    """パスワードリストファイルを読み込む"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"パスワードリストの読み込みエラー: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(
        description='PDFファイルのパスワードを解除するツール',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用例:
  # 単一ファイルのパスワード解除
  python pdf_password_remover.py input.pdf -o output.pdf -p mypassword
  
  # パスワードを対話的に入力
  python pdf_password_remover.py input.pdf -o output.pdf
  
  # 一般的なパスワードを自動試行
  python pdf_password_remover.py input.pdf -o output.pdf --try-common
  
  # ディレクトリ内のPDFを一括処理
  python pdf_password_remover.py input_dir/ -o output_dir/ -p mypassword --batch
  
  # パスワードリストファイルを使用
  python pdf_password_remover.py input.pdf -o output.pdf --password-list passwords.txt
        '''
    )
    
    parser.add_argument('input', help='入力PDFファイルまたはディレクトリ')
    parser.add_argument('-o', '--output', help='出力PDFファイルまたはディレクトリ')
    parser.add_argument('-p', '--password', help='PDFのパスワード')
    parser.add_argument('--batch', action='store_true', 
                       help='ディレクトリ内のPDFを一括処理')
    parser.add_argument('-r', '--recursive', action='store_true',
                       help='サブディレクトリも含めて処理（--batchと併用）')
    parser.add_argument('--try-common', action='store_true',
                       help='一般的なパスワードを自動的に試す')
    parser.add_argument('--password-list', 
                       help='試すパスワードのリストファイル（1行1パスワード）')
    parser.add_argument('--check-only', action='store_true',
                       help='PDFが暗号化されているかチェックのみ')
    
    args = parser.parse_args()
    
    remover = PDFPasswordRemover()
    
    # チェックのみモード
    if args.check_only:
        if os.path.isfile(args.input):
            is_encrypted = remover.check_if_encrypted(args.input)
            if is_encrypted:
                print(f"✓ {args.input} は暗号化されています")
            else:
                print(f"✗ {args.input} は暗号化されていません")
        else:
            print("エラー: 入力ファイルが見つかりません")
        return
    
    # 出力パスの設定
    if not args.output:
        if args.batch:
            args.output = args.input + '_unlocked'
        else:
            base_name = os.path.splitext(args.input)[0]
            args.output = f"{base_name}_unlocked.pdf"
    
    # バッチ処理モード
    if args.batch:
        if not os.path.isdir(args.input):
            print("エラー: バッチモードでは入力はディレクトリである必要があります")
            return
        
        # パスワードの取得
        if not args.password:
            import getpass
            args.password = getpass.getpass("パスワードを入力してください: ")
        
        remover.process_batch(args.input, args.output, args.password, args.recursive)
        print(f"\n処理完了: 成功 {remover.processed_count}, 失敗 {remover.failed_count}")
        return
    
    # 単一ファイル処理
    if not os.path.isfile(args.input):
        print("エラー: 入力ファイルが見つかりません")
        return
    
    # 暗号化チェック
    if not remover.check_if_encrypted(args.input):
        print("このPDFは暗号化されていません")
        return
    
    # パスワードリストを使用
    if args.password_list:
        password_list = load_password_list(args.password_list)
        if password_list:
            found_password = remover.try_common_passwords(
                args.input, args.output, password_list
            )
            if found_password:
                print(f"\n✓ パスワード解除成功！")
                print(f"  使用されたパスワード: {found_password}")
                print(f"  出力ファイル: {args.output}")
            else:
                print("\n✗ リスト内のパスワードでは解除できませんでした")
        return
    
    # 一般的なパスワードを試す
    if args.try_common:
        found_password = remover.try_common_passwords(args.input, args.output)
        if found_password:
            print(f"\n✓ パスワード解除成功！")
            print(f"  使用されたパスワード: {found_password}")
            print(f"  出力ファイル: {args.output}")
        else:
            print("\n✗ 一般的なパスワードでは解除できませんでした")
            print("正しいパスワードを -p オプションで指定してください")
        return
    
    # パスワードの取得
    if not args.password:
        import getpass
        args.password = getpass.getpass("パスワードを入力してください: ")
    
    # パスワード解除実行
    if remover.remove_password(args.input, args.output, args.password):
        print(f"\n✓ パスワード解除成功！")
        print(f"  出力ファイル: {args.output}")
    else:
        print("\n✗ パスワード解除に失敗しました")


if __name__ == "__main__":
    main()
