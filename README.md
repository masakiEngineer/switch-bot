# Switchbot AI制御システム

自然言語でSwitchbotデバイスを操作できるAIエージェントシステムです。SlackボットとしてSlackから操作したり、スケジュール機能で自動化できます。

## 主な機能

### 1. デバイス操作
- **ON/OFF**: デバイスの電源操作
- **明るさ調整**: シーリングライトの明るさを1-100%で調整
- **色温度調整**: 暖色、昼白色、寒色など色温度の変更
- **カーテン操作**: 開閉
- **スマートロック**: 施錠/解錠

### 2. Slackボット
- Slackメッセージで自然言語操作
- ポーリング方式（SLACK_BOT_TOKENのみで動作）
- スレッドで返信

### 3. スケジュール機能
- 指定時刻にデバイスを自動操作
- 明るさや色温度も設定可能
- schedules.jsonに保存

## ファイル構成

```
Switchbot/
├── .env                    # 環境変数（トークン、APIキー）
├── requirements.txt        # 依存パッケージ
├── utils.py               # Switchbot API操作
├── agent.py               # AIエージェント（OpenAI）
├── scheduler.py           # スケジュール管理
├── slack_bot.py           # Slackボット
├── test_agent.py          # テストスクリプト
├── schedules.json         # スケジュール保存ファイル（自動生成）
└── README.md              # このファイル
```

## セットアップ

### 1. パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env`ファイルを作成し、以下を設定：

```env
# Switchbot
SWITCH_BOT_TOKEN=your_switchbot_token
SWITCH_BOT_CLIENT_SECRET=your_switchbot_secret

# Slack
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL_ID=C0XXXXXXXXX

# OpenAI
OPENAI_API_KEY=sk-proj-your-openai-api-key
```

## 使い方

### 基本的な使い方（対話モード）

```bash
python agent.py
```

例：
```
あなた: シーリングライトをつけて
エージェント: OK: 白いシーリングライトをonしました！

あなた: 明るさを50%にして
エージェント: OK: 白いシーリングライトの明るさを50%に設定しました！

あなた: 暖色にして
エージェント: OK: 白いシーリングライトの色温度をwarmに設定しました！
```

### Slackボット

```bash
python slack_bot.py
```

Slackチャンネルでメッセージを送信するだけで操作できます：

```
あなた: シーリングライトをつけて
Bot: OK: 白いシーリングライトをonしました！

あなた: 7時にシーリングライトをつけて
Bot: OK: 白いシーリングライトを07:00にturnOnするスケジュールを追加しました！

あなた: スケジュール一覧を見せて
Bot: 登録済みスケジュール:
1. 07:00 - 白いシーリングライト - turnOn
```

## 対応コマンド例

### 基本操作
- 「デバイス一覧を見せて」
- 「シーリングライトをつけて」
- 「シーリングライトを消して」
- 「カーテンを開けて」
- 「プラグをオンにして」

### 明るさ調整
- 「シーリングライトの明るさを50%にして」
- 「シーリングライトを半分の明るさにして」
- 「明るさを最大にして」
- 「暗くして」（AIが適切な値を判断）

### 色温度調整
- 「シーリングライトを暖色にして」
- 「シーリングライトを白にして」
- 「シーリングライトを昼白色にして」

### スケジュール
- 「毎朝7時にシーリングライトをつけて」
- 「19時にシーリングライトを暖色50%にして」
- 「スケジュール一覧を見せて」

## 技術スタック

- **Python 3.10+**
- **OpenAI GPT-4o-mini**: 自然言語理解（Function Calling使用）
- **Switchbot API v1.1**: デバイス操作
- **Slack SDK**: Slackボット
- **schedule**: スケジュール機能

## APIリファレンス

### utils.py

```python
# デバイス一覧取得
get_devices()

# デバイス操作
control_device(device_id, command, parameter="default")

# 明るさ設定（1-100）
set_ceiling_light_brightness(device_id, brightness)

# 色温度設定（2700-6500K または warm/neutral/cool）
set_ceiling_light_color_temp(device_id, color_temp)
```

### scheduler.py

```python
# スケジュール追加
add_schedule(time_str, device_id, device_name, action, **kwargs)

# スケジュール一覧取得
get_schedules()

# スケジュール削除
remove_schedule(index)
```

## Oracle Cloud Always Free Tierへのデプロイ（常時稼働・完全無料）

Oracle Cloud Always Free Tierを使って、ボットを**完全無料で24時間365日**稼働させることができます。

### 特徴
- **完全無料**（Always Free枠はずっと無料）
- **24時間365日稼働**
- **期限なし**

### 1. Oracle Cloudアカウント作成

1. **Oracle Cloudにアクセス**: https://www.oracle.com/cloud/free/
2. **Start for free** をクリック
3. アカウント情報を入力して登録（クレジットカード登録が必要ですが、Always Free枠は課金されません）

### 2. VM（仮想マシン）の作成

1. **Oracle Cloudコンソール**にログイン
2. **Compute** > **Instances** に移動
3. **Create Instance** をクリック
4. 以下の設定で作成：
   - **Name**: switchbot-server（任意）
   - **Image**: Ubuntu 22.04（または最新のUbuntu）
   - **Shape**: VM.Standard.E2.1.Micro（Always Free対象）
   - **SSH Keys**: SSH公開鍵をアップロードまたは自動生成
5. **Create** をクリック

### 3. ファイアウォール設定（任意）

SSH接続のみ必要なので、デフォルト設定でOKです。

### 4. VMにSSH接続

```bash
# Windows（Git Bash、PowerShell、またはWSL）
ssh -i path/to/private-key ubuntu@あなたのVMのパブリックIP

# 例
ssh -i ~/.ssh/oracle_vm_key ubuntu@123.456.789.012
```

### 5. セットアップスクリプトを実行

VMにログインしたら、以下のコマンドを実行：

```bash
# セットアップスクリプトをダウンロード
wget https://raw.githubusercontent.com/masakiEngineer/switch-bot/main/setup_oracle.sh

# 実行権限を付与
chmod +x setup_oracle.sh

# スクリプトを実行
./setup_oracle.sh
```

スクリプトが以下を自動で行います：
1. システムアップデート
2. Python3とgitのインストール
3. リポジトリのクローン
4. 仮想環境の作成
5. パッケージのインストール
6. 環境変数ファイルの作成（手動入力が必要）
7. systemdサービスとして登録

### 6. 環境変数の設定

セットアップスクリプト実行中に`.env`ファイルの編集が求められます。
以下の内容を入力してください：

```env
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL_ID=C0123456789
SWITCH_BOT_TOKEN=your-switchbot-token
SWITCH_BOT_CLIENT_SECRET=your-switchbot-secret
OPENAI_API_KEY=sk-your-openai-api-key
```

保存方法（nanoエディタ）：
1. 内容を入力
2. `Ctrl + O` で保存
3. `Enter` で確認
4. `Ctrl + X` で終了

### 7. サービスの確認

セットアップが完了したら、サービスが起動しているか確認：

```bash
# サービスの状態を確認
sudo systemctl status switchbot-slack

# リアルタイムでログを確認
sudo journalctl -u switchbot-slack -f
```

### デプロイ後のメンテナンス

```bash
# サービスの再起動
sudo systemctl restart switchbot-slack

# サービスの停止
sudo systemctl stop switchbot-slack

# サービスの起動
sudo systemctl start switchbot-slack

# ログ確認
sudo journalctl -u switchbot-slack -f

# 環境変数の編集
nano ~/switch-bot/.env
sudo systemctl restart switchbot-slack  # 編集後は再起動が必要
```

### Oracle Cloud固有のトラブルシューティング

#### サービスが起動しない場合

```bash
# ログを確認
sudo journalctl -u switchbot-slack -n 50

# 手動で起動してエラーを確認
cd ~/switch-bot
source venv/bin/activate
python slack_bot.py
```

#### 環境変数が正しく読み込まれない場合

```bash
# .envファイルの内容を確認
cat ~/switch-bot/.env

# パーミッションを確認
ls -la ~/switch-bot/.env
```

## トラブルシューティング

### Slackボットが反応しない
1. Bot Token Scopesを確認（channels:history, channels:read, chat:write）
2. ボットをチャンネルに招待（/invite @bot名）
3. .envのSLACK_BOT_TOKENとSLACK_CHANNEL_IDを確認

### デバイス操作が失敗する
1. SWITCH_BOT_TOKENが正しいか確認
2. デバイスがオンラインか確認
3. `python utils.py`でデバイス一覧を取得して確認

### スケジュールが実行されない
1. slack_bot.pyが起動しているか確認
2. schedules.jsonが正しく保存されているか確認
3. 時刻形式がHH:MM（例：07:00）か確認
