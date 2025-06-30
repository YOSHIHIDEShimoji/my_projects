import os
from PyPDF2 import PdfReader, PdfWriter
from pdf2docx import Converter

# === 共通設定 ===
input_dir = 'pdfs'         # PDFファイルがあるフォルダ
unlocked_dir = 'unlocked'  # パスワード解除後のPDFを一時保存
output_dir = 'output'      # Wordファイル出力先
password = '500101'        # 共通パスワード

# === フォルダ作成 ===
os.makedirs(unlocked_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# === パスワード解除関数 ===
def unlock_pdf(input_path, output_path):
    try:
        reader = PdfReader(input_path)
        if reader.is_encrypted:
            reader.decrypt(password)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        with open(output_path, "wb") as f:
            writer.write(f)
        print(f'🔓 パスワード解除成功: {os.path.basename(input_path)}')
        return True
    except Exception as e:
        print(f'❌ パスワード解除失敗: {input_path} → {e}')
        return False

# === PDF → Word 変換関数 ===
def convert_pdf_to_word(pdf_path, docx_path):
    try:
        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()
        print(f'✅ Word変換成功: {os.path.basename(docx_path)}')
    except Exception as e:
        print(f'❌ Word変換失敗: {pdf_path} → {e}')

# === メイン処理 ===
for file_name in os.listdir(input_dir):
    if file_name.endswith('.pdf'):
        pdf_path = os.path.join(input_dir, file_name)
        unlocked_path = os.path.join(unlocked_dir, file_name)
        docx_path = os.path.join(output_dir, file_name.replace('.pdf', '.docx'))

        # パスワード解除（失敗したらスキップ）
        if unlock_pdf(pdf_path, unlocked_path):
            convert_pdf_to_word(unlocked_path, docx_path)

print('\n🎉 すべてのPDF処理が完了しました。')
