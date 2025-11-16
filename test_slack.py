"""Slackボットの動作テスト"""
import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()

slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

print("=== Slack接続テスト ===")
print(f"チャンネルID: {CHANNEL_ID}")

try:
    # ボットの情報を取得
    response = slack_client.auth_test()
    print("OK: Bot接続成功")
    print(f"  ボット名: {response['user']}")
    print(f"  ボットID: {response['user_id']}")
    print(f"  チーム: {response['team']}")

    # テストメッセージを送信
    print("\nテストメッセージを送信中...")
    slack_client.chat_postMessage(
        channel=CHANNEL_ID,
        text="[テスト] ボットは正常に動作しています！"
    )
    print("OK: メッセージ送信成功")

    # 最新のメッセージを取得
    print("\nチャンネル履歴を取得中...")
    history = slack_client.conversations_history(
        channel=CHANNEL_ID,
        limit=3
    )
    print(f"OK: 履歴取得成功（{len(history['messages'])}件）")

    print("\nOK: すべてのテストが成功しました！")

except SlackApiError as e:
    print(f"\nエラー: {e.response['error']}")
    print(f"  詳細: {e}")
except Exception as e:
    print(f"\n予期しないエラー: {e}")
