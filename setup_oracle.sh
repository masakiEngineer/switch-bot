#!/bin/bash
# Oracle Cloud Always Free VM セットアップスクリプト

set -e

echo "=== Switchbot Slack Bot セットアップ ==="
echo ""

# 1. システムアップデート
echo "[1/7] システムをアップデート中..."
sudo apt update && sudo apt upgrade -y

# 2. 必要なパッケージをインストール
echo "[2/7] 必要なパッケージをインストール中..."
sudo apt install -y python3 python3-pip python3-venv git

# 3. リポジトリをクローン
echo "[3/7] GitHubからリポジトリをクローン中..."
cd ~
if [ -d "switch-bot" ]; then
    echo "既存のswitch-botディレクトリを削除します..."
    rm -rf switch-bot
fi
git clone https://github.com/masakiEngineer/switch-bot.git
cd switch-bot

# 4. 仮想環境を作成
echo "[4/7] Python仮想環境を作成中..."
python3 -m venv venv
source venv/bin/activate

# 5. 依存パッケージをインストール
echo "[5/7] Pythonパッケージをインストール中..."
pip install --upgrade pip
pip install -r requirements.txt

# 6. .envファイルの作成を促す
echo "[6/7] 環境変数ファイルを作成してください..."
echo ""
echo ".envファイルを作成する必要があります。"
echo "以下のコマンドでファイルを編集してください："
echo ""
echo "  nano ~/.switch-bot/.env"
echo ""
echo "以下の内容を入力してください："
echo ""
cat .env.example
echo ""
read -p "Enterキーを押すとエディタが開きます..."

nano .env

# 7. systemdサービスとして登録
echo "[7/7] systemdサービスとして登録中..."
sudo cp switchbot-slack.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable switchbot-slack.service
sudo systemctl start switchbot-slack.service

echo ""
echo "=== セットアップ完了！ ==="
echo ""
echo "サービスの状態を確認:"
echo "  sudo systemctl status switchbot-slack"
echo ""
echo "ログを確認:"
echo "  sudo journalctl -u switchbot-slack -f"
echo ""
echo "サービスの再起動:"
echo "  sudo systemctl restart switchbot-slack"
echo ""
