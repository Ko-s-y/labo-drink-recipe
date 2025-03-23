import os
import openai

from dotenv import load_dotenv
from flask import Flask, request, render_template_string
from pyngrok import ngrok

# .envファイルから環境変数を読み込む
load_dotenv()

# OpenAI と ngrok の API キーを取得
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
NGROK_AUTH_TOKEN = os.environ.get("NGROK_AUTH_TOKEN")

# キーが入っているかチェック
if not OPENAI_API_KEY:
    raise ValueError("環境変数 OPENAI_API_KEY が設定されていません.")
if not NGROK_AUTH_TOKEN:
    raise ValueError("環境変数 NGROK_AUTH_TOKEN が設定されていません.")

openai.api_key = OPENAI_API_KEY

# Flask アプリ作成
app = Flask(__name__)

# ngrok の認証トークン設定 & トンネル作成
ngrok.set_auth_token(NGROK_AUTH_TOKEN)
public_url = ngrok.connect(5000)
print(" * ngrok tunnel URL:", public_url.public_url)

# ========== OpenAI API でレシピ生成する関数 ==========
def generate_recipe_with_openai(drink_name: str):
    """
    OpenAI (GPT) を使って、指定のドリンクに関するレシピを生成する。
    シンプルに text-davinci-003 を使った例。
    """
    prompt = f"""
    あなたはプロのバーテンダーです。
    {drink_name} というドリンクについて、レシピと作り方を日本語で提案してください。
    必要に応じてアレンジも加えてください。
    """
    
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=200,
            temperature=0.7,
        )
        text = response.choices[0].text.strip()
        return text
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return "AI生成に失敗しました。"

# ========== HTML フォーム (テンプレート文字列) ==========
html_form = """
<!DOCTYPE html>
<html>
<head>
    <title>ドリンクレシピ検索</title>
</head>
<body>
    <h1>ドリンクレシピ生成フォーム (AIのみ)</h1>
    <form method="POST" action="/generate">
        <label for="drink_name">ドリンク名：</label>
        <input type="text" id="drink_name" name="drink_name" required>
        <button type="submit">レシピ生成</button>
    </form>
</body>
</html>
"""

# ========== ルーティング ==========
@app.route("/", methods=["GET"])
def index():
    """フォームを表示"""
    return html_form

@app.route("/generate", methods=["POST"])
def generate():
    """ドリンク名を受け取ってAIレシピを生成して返す"""
    drink_name = request.form.get("drink_name", "").strip()
    if not drink_name:
        return "ドリンク名が入力されていません。"

    # 常にOpenAIでレシピ生成
    ai_text = generate_recipe_with_openai(drink_name)

    # HTMLで結果を返す
    response_html = f"""
    <html>
    <head><title>レシピ結果</title></head>
    <body>
        <h1>{drink_name} のレシピ (AI生成)</h1>
        <p style="white-space: pre-wrap;">{ai_text}</p>
        <br>
        <a href="/">別のドリンクを生成</a>
    </body>
    </html>
    """
    return response_html

if __name__ == "__main__":
    # Flaskサーバー起動
    app.run(port=5000, debug=True)
