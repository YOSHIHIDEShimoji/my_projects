import os
import whisper
import time
import torch
import argparse
from pathlib import Path
import sys
import platform

# tqdmがインストールされているか確認
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

def transcribe_audio():
    """Whisperを使用して音声を文字起こしする関数
    
    利用可能なモデル:
    - 標準モデル: tiny, base, small, medium, large
    - 高精度モデル: large-v2, large-v3
    - 英語特化モデル: tiny.en, base.en, small.en, medium.en, large.en
    """
    # コマンドライン引数のパーサーを設定
    parser = argparse.ArgumentParser(description="Whisperで音声ファイルを文字起こしします")
    parser.add_argument("-f", "--file", help="音声ファイルのパス")
    parser.add_argument("-m", "--model", 
                        choices=["tiny", "base", "small", "medium", "large", "large-v2", "large-v3", 
                                "tiny.en", "base.en", "small.en", "medium.en", "large.en"], 
                        help="使用するWhisperモデル")
    parser.add_argument("-o", "--output", help="出力先ディレクトリ")
    parser.add_argument("-d", "--device", choices=["cpu", "cuda"], help="使用するデバイス（CPU/GPU）")
    args = parser.parse_args()
    
    # CPU情報を取得・表示（Linuxのみ対応）
    def get_cpu_info():
        try:
            # /proc/cpuinfoからmodel nameを取得
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('model name'):
                        return line.split(':')[1].strip()
        except:
            # 取得できない場合は簡易情報
            return "CPU情報が取得できません"
    
    print(f"CPU情報: {get_cpu_info()}")
    
    # GPU情報を表示
    if torch.cuda.is_available():
        gpu_info = torch.cuda.get_device_name(0)
        print(f"GPU情報: {gpu_info}")
        gpu_available = True
    else:
        print("GPU情報: GPUが利用できません")
        gpu_available = False
    
    # デバイス選択
    if args.device:
        device = args.device
        print(f"コマンドライン引数で指定されたデバイス: {device}")
        # 指定されたデバイスが利用不可の場合の処理
        if device == "cuda" and not gpu_available:
            print("警告: GPUが利用できないため、CPUに切り替えます")
            device = "cpu"
    else:
        # ユーザーに選択させる
        while True:
            device_choice = input("処理に使用するデバイスを選択してください（gpu/cpu）: ").strip().lower()
            if device_choice in ["gpu", "cuda"]:
                if gpu_available:
                    device = "cuda"
                    break
                else:
                    print("GPUが利用できません。CPUを選択してください。")
            elif device_choice in ["cpu"]:
                device = "cpu"
                break
            else:
                print("無効な入力です。'gpu' または 'cpu' を入力してください。")
    
    print(f"使用デバイス: {device}")
    
    # ファイルパスの取得（コマンドライン引数またはユーザー入力）
    file_path = args.file
    if not file_path:
        while True:
            file_path = input("音声ファイルのパスを入力してください: ").strip()
            if os.path.exists(file_path):
                print(f"ファイルが見つかりました - {file_path}\n")
                break
            else:
                print(f"エラー: ファイルが見つかりません - {file_path}。もう一度入力してください。\n")
    
    # モデルの選択（コマンドライン引数またはユーザー入力）
    selected_model = args.model
    if not selected_model:
        valid_models = {
            "t": "tiny", "b": "base", "s": "small", "m": "medium", "l": "large",
            "lv2": "large-v2", "lv3": "large-v3", 
            "te": "tiny.en", "be": "base.en", "se": "small.en", "me": "medium.en", "le": "large.en"
        }
        
        print("Whisperモデルを選択してください（コードで選択）:")
        print("-- 標準モデル（多言語対応） --")
        print("t: tiny (軽量・低精度)")
        print("b: base (軽量・標準精度)")
        print("s: small (中量・標準精度)")
        print("m: medium (重量・高精度)")
        print("l: large (最重量・最高精度)")
        print("\n-- 高精度モデル --")
        print("lv2: large-v2 (改良版・高精度)")
        print("lv3: large-v3 (最新版・最高精度)")
        print("\n-- 英語特化モデル --")
        print("te: tiny.en (英語特化・軽量)")
        print("be: base.en (英語特化・標準)")
        print("se: small.en (英語特化・中量)")
        print("me: medium.en (英語特化・重量)")
        print("le: large.en (英語特化・最重量)")
        
        while True:
            selected_key = input("モデルのコードを入力してください: ").strip().lower()
            if selected_key in valid_models:
                selected_model = valid_models[selected_key]
                break
            else:
                print(f"エラー: '{selected_key}' は無効な入力です。上記の選択肢から入力してください。")
    
    print(f"選択されたモデル: {selected_model}\n\nしばらくお待ちください\n")
    
    # 出力先ディレクトリの設定
    if args.output:
        # コマンドライン引数で指定された場合はそれを使用
        output_dir = Path(args.output)
    else:
        # 指定がない場合はカレントディレクトリ内のdataフォルダを使用
        data_dir = Path(os.getcwd()) / "data"
        output_dir = data_dir
    
    # ディレクトリが存在しない場合は作成
    if not output_dir.exists():
        print(f"出力先ディレクトリ {output_dir} を作成します")
        output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 処理開始時間を記録
        start_time = time.time()
        
        # Whisperモデルをロード（明示的にデバイスを指定）
        print(f"モデル '{selected_model}' をロードしています...")
        
        # モデルの種類に応じた説明を表示
        if selected_model.endswith('.en'):
            print("英語特化モデルを使用します。英語の音声で最高の精度が得られます。")
        elif selected_model == 'large-v2':
            print("Large-v2モデルを使用します。標準のlargeモデルより高精度で、多言語対応が強化されています。")
        elif selected_model == 'large-v3':
            print("Large-v3モデルを使用します。最新の高精度モデルです。")
            
        # モデルロード
        try:
            model = whisper.load_model(selected_model, device=device)
            print(f"モデルを {device} にロードしました")
        except Exception as e:
            print(f"モデルのロード中にエラーが発生しました: {e}")
            print("モデルが利用できない場合は、OpenAI Whisperの最新バージョンをインストールしてください。")
            print("pip install --upgrade openai-whisper")
            raise
        
        # 音声ファイルを文字起こし
        print("文字起こしを開始します...")
        
        # オリジナルのWhisper transcribe関数をラップして進捗表示を追加
        def transcribe_with_progress(audio_path, model, model_name):
            # 音声ファイルの読み込み (ffmpegでデコード)
            print("音声ファイルを読み込み中...")
            audio = whisper.load_audio(audio_path)
            # 音声を16kHzにリサンプリング
            audio = whisper.pad_or_trim(audio)
            
            # メルスペクトログラムの計算
            print("音声データを処理中...")
            mel = whisper.log_mel_spectrogram(audio).to(model.device)
            
            # 言語の検出
            print("言語を検出中...")
            _, probs = model.detect_language(mel)
            detected_lang = max(probs, key=probs.get)
            print(f"検出された言語: {detected_lang} (信頼度: {probs[detected_lang]:.2%})")
            
            # 音声の長さに基づいて処理の単位数を概算
            # 音声の長さ（秒）
            audio_duration = len(audio) / 16000  # 16kHzでサンプリングされた音声
            print(f"音声の長さ: {audio_duration:.2f}秒")
            
            # 文字起こし
            print("文字起こしを実行中...")
            
            if TQDM_AVAILABLE:
                # 進捗バーを表示（音声の長さに比例）
                # おおよその進捗を表示するための目安として使用
                with tqdm(total=100, desc="処理中", unit="%") as pbar:
                    # モデルサイズに基づいて進捗更新間隔を調整
                    # ダミーの進捗更新（実際の進捗とは一致しない可能性があります）
                    result = model.transcribe(audio_path)
                    pbar.update(100)  # 最終的に100%まで更新
                    
            else:
                # tqdmが利用できない場合は簡易的な進捗表示
                print("進捗: 0%", end="\r")
                sys.stdout.flush()
                
                result = model.transcribe(audio_path)
                
                print("進捗: 100%", end="\r")
                sys.stdout.flush()
                print("\n処理完了しました!")
            
            return result
        
        # 進捗表示付きの文字起こしを実行
        result = transcribe_with_progress(file_path, model, selected_model)
        
        # 処理終了時間を記録
        end_time = time.time()
        elapsed_seconds = end_time - start_time
        
        # 処理時間を時間、分、秒に変換
        hours, remainder = divmod(elapsed_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # 元の音声ファイル名を取得
        base_name = Path(file_path).stem
        
        # 保存ファイル名を生成
        output_file = f"{base_name}_whisper_{selected_model}.txt"
        output_path = output_dir / output_file
        
        # 結果を保存
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result["text"])
        
        print(f"\n文字起こし結果を '{output_path}' に保存しました。")
        print(f"処理時間: {int(hours)}時間 {int(minutes)}分 {seconds:.2f}秒")
        print(f"使用デバイス: {device}")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        # GPUメモリをクリア（CUDA使用時のみ）
        if torch.cuda.is_available() and device == "cuda":
            torch.cuda.empty_cache()
            print("GPUメモリをクリアしました")

if __name__ == "__main__":
    transcribe_audio()