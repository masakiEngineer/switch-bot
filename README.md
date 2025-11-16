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

## Railway.appへのデプロイ（常時稼働）

Railway.appの無料枠を使って、ボットを24時間稼働させることができます。

### 1. 前提条件

- GitHubアカウント
- Railway.appアカウント（https://railway.app/ でGitHubアカウントでサインアップ）

### 2. GitHubにコードをプッシュ

```bash
# Gitリポジトリを初期化（まだの場合）
git init
git add .
git commit -m "Initial commit"

# GitHubにリポジトリを作成してプッシュ
git remote add origin https://github.com/あなたのユーザー名/switchbot.git
git branch -M main
git push -u origin main
```

### 3. Railway.appでデプロイ

1. **Railway.appにログイン**: https://railway.app/
2. **New Project** をクリック
3. **Deploy from GitHub repo** を選択
4. **GitHubリポジトリ**を選択
5. **Deploy Now** をクリック

### 4. 環境変数の設定

Railwayのプロジェクトページで：

1. **Variables** タブを開く
2. 以下の環境変数を追加：

```
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL_ID=C0123456789
SWITCH_BOT_TOKEN=your-switchbot-token
SWITCH_BOT_CLIENT_SECRET=your-switchbot-secret
OPENAI_API_KEY=sk-your-openai-api-key
```

### 5. デプロイ完了

環境変数を設定すると、自動的に再デプロイされ、ボットが起動します。
**Deployments** タブでログを確認できます。

### 6. 無料枠について

Railway.appの無料枠：
- **月500時間**（約20日分）の実行時間
- 無料枠を超えると自動停止
- クレジットカード登録で$5/月の無料クレジット付与

### デプロイ後のメンテナンス

- **ログ確認**: Railwayのダッシュボード > Deployments > Logs
- **再起動**: Deployments > 右上の3点メニュー > Restart
- **環境変数の変更**: Variables タブで編集

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

## ライセンス

MIT License

## 作者

Created with Claude Code
