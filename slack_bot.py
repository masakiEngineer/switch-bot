"""Slackポーリング方式ボット - Switchbot操作"""
import os
import time
import threading
from datetime import datetime
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from agent import process_user_request
import schedule
from scheduler import load_schedules, register_schedule, get_schedules

# 環境変数を読み込む
load_dotenv()

# Slackクライアントを初期化
slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

# 最後に処理したメッセージのタイムスタンプ
last_processed_ts = None
bot_user_id = None

# スレッドごとの会話履歴を保存
# { "thread_ts": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}] }
thread_conversations = {}

# スレッドごとの最後に処理したタイムスタンプ
# { "thread_ts": "ts" }
thread_last_ts = {}

def get_bot_user_id():
    """ボット自身のユーザーIDを取得"""
    try:
        response = slack_client.auth_test()
        return response["user_id"]
    except SlackApiError as e:
        print(f"エラー: ボットユーザーIDの取得に失敗 - {e}")
        return None

def get_new_messages():
    """新しいメッセージを取得"""
    global last_processed_ts

    try:
        # チャンネルの履歴を取得
        kwargs = {
            "channel": CHANNEL_ID,
            "limit": 10  # 直近10件を取得
        }

        # 前回のタイムスタンプがある場合、それ以降のみ取得
        if last_processed_ts:
            kwargs["oldest"] = last_processed_ts
            print(f"[DEBUG] oldest={last_processed_ts}で検索")

        response = slack_client.conversations_history(**kwargs)
        messages = response["messages"]

        # デバッグ: メッセージ数をログ出力
        print(f"[DEBUG] conversations_history: {len(messages)}件取得")

        # 既に処理済みのメッセージを除外
        new_messages = []
        for msg in messages:
            if last_processed_ts and msg["ts"] <= last_processed_ts:
                # 既に処理済み
                continue
            new_messages.append(msg)

        if new_messages:
            print(f"[DEBUG] 新しいメッセージ: {len(new_messages)}件")
            # メッセージは新しい順なので、最初のメッセージのtsを保存
            last_processed_ts = new_messages[0]["ts"]

        return new_messages

    except SlackApiError as e:
        print(f"エラー: メッセージ取得に失敗 - {e}")
        return []

def get_thread_replies(thread_ts):
    """スレッド内の新しい返信を取得"""
    try:
        # スレッドの返信を取得
        response = slack_client.conversations_replies(
            channel=CHANNEL_ID,
            ts=thread_ts,
            oldest=thread_last_ts.get(thread_ts, thread_ts)  # 前回のタイムスタンプ以降
        )

        messages = response["messages"]

        # 最初のメッセージ（親メッセージ）は除外
        # 新しい返信のみを返す
        new_replies = [msg for msg in messages if msg["ts"] != thread_ts]

        # 最後に処理したタイムスタンプを更新
        if new_replies:
            thread_last_ts[thread_ts] = new_replies[-1]["ts"]

        return new_replies

    except SlackApiError as e:
        print(f"エラー: スレッド返信取得に失敗 - {e}")
        return []

def send_message(text, thread_ts=None):
    """Slackにメッセージを送信"""
    try:
        slack_client.chat_postMessage(
            channel=CHANNEL_ID,
            text=text,
            thread_ts=thread_ts  # スレッドで返信
        )
    except SlackApiError as e:
        print(f"エラー: メッセージ送信に失敗 - {e}")

def process_message(message, is_thread_reply=False):
    """メッセージを処理

    Args:
        message: Slackメッセージ
        is_thread_reply: スレッド内の返信かどうか
    """
    global bot_user_id, thread_conversations

    # ボットのユーザーIDを取得（初回のみ）
    if bot_user_id is None:
        bot_user_id = get_bot_user_id()

    # デバッグログ
    print(f"[DEBUG] process_message: user={message.get('user')}, bot={bot_user_id}, subtype={message.get('subtype')}, text={message.get('text', '')[:30]}")

    # ボット自身のメッセージは無視
    if message.get("user") == bot_user_id:
        print(f"[DEBUG] ボット自身のメッセージをスキップ")
        return

    # サブタイプがあるメッセージ（編集、削除など）は無視
    if "subtype" in message:
        print(f"[DEBUG] サブタイプメッセージをスキップ: {message.get('subtype')}")
        return

    text = message.get("text", "").strip()
    ts = message.get("ts")
    thread_ts = message.get("thread_ts", ts)  # スレッドのタイムスタンプ

    if not text:
        print(f"[DEBUG] 空のメッセージをスキップ")
        return

    # スレッド内の返信かどうかを表示
    thread_indicator = "[スレッド返信] " if is_thread_reply else ""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {thread_indicator}受信: {text}")

    try:
        # 会話履歴を取得（スレッドの場合）
        conversation_history = None
        if is_thread_reply or thread_ts != ts:
            # スレッド内の返信の場合、会話履歴を使用
            conversation_history = thread_conversations.get(thread_ts, [])
            if conversation_history:
                print(f"  → 会話履歴を参照: {len(conversation_history)}件")
        else:
            # 新しいメインメッセージの場合、会話履歴をクリア
            thread_conversations[thread_ts] = []

        # ユーザーのメッセージを履歴に追加
        thread_conversations.setdefault(thread_ts, []).append({
            "role": "user",
            "content": text
        })

        # AIエージェントで処理
        response = process_user_request(text, conversation_history)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 応答: {response}")

        # ボットの応答を履歴に追加
        thread_conversations[thread_ts].append({
            "role": "assistant",
            "content": response
        })

        # スレッドで返信
        send_message(response, thread_ts=thread_ts)

    except Exception as e:
        error_msg = f"エラーが発生しました: {str(e)}"
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {error_msg}")
        send_message(error_msg, thread_ts=thread_ts)

def run_scheduler_thread():
    """スケジューラーをバックグラウンドで実行"""
    # スケジュールを読み込み
    load_schedules()
    schedules_list = get_schedules()

    # 既存のスケジュールを登録
    for item in schedules_list:
        register_schedule(item)

    print(f"スケジューラー起動: {len(schedules_list)}件のスケジュールを読み込みました")

    # スケジューラーを実行
    while True:
        schedule.run_pending()
        time.sleep(10)  # 10秒ごとにチェック

def main():
    """メインループ"""
    global last_processed_ts, bot_user_id

    print("=== Switchbot Slackボット（ポーリング方式） ===")
    print(f"チャンネルID: {CHANNEL_ID}")

    # ボットユーザーIDを取得
    bot_user_id = get_bot_user_id()
    if not bot_user_id:
        print("エラー: ボットの初期化に失敗しました")
        return

    print(f"ボットユーザーID: {bot_user_id}")

    # スケジューラーを別スレッドで起動
    scheduler_thread = threading.Thread(target=run_scheduler_thread, daemon=True)
    scheduler_thread.start()

    print("監視を開始します...\n")

    # 初回起動時は最新メッセージのタイムスタンプを取得（過去メッセージは処理しない）
    try:
        initial_response = slack_client.conversations_history(
            channel=CHANNEL_ID,
            limit=1
        )
        if initial_response["messages"]:
            last_processed_ts = initial_response["messages"][0]["ts"]
            print(f"初期化: 最新メッセージts={last_processed_ts}\n")
        else:
            last_processed_ts = None
            print("初期化: チャンネルにメッセージがありません\n")
    except Exception as e:
        print(f"初期化エラー: {e}\n")
        last_processed_ts = None

    polling_interval = 3  # ポーリング間隔（秒）

    # アクティブなスレッドのリスト（スレッドTSのセット）
    active_threads = set()

    try:
        while True:
            # 1. メインチャンネルの新しいメッセージを取得
            messages = get_new_messages()

            print(f"[DEBUG] ポーリング: {len(messages)}件のメッセージ, アクティブスレッド: {len(active_threads)}件")

            # メッセージは新しい順なので、古い順に処理するため反転
            for message in reversed(messages):
                ts = message.get("ts")
                thread_ts = message.get("thread_ts")

                # メインメッセージの場合
                if not thread_ts or thread_ts == ts:
                    print(f"[DEBUG] メインメッセージを処理: ts={ts}")
                    process_message(message, is_thread_reply=False)

                    # このメッセージがスレッドの親になる可能性があるので、アクティブなスレッドに追加
                    active_threads.add(ts)

            # 2. アクティブなスレッドの返信をチェック
            for thread_ts in list(active_threads):
                replies = get_thread_replies(thread_ts)

                if replies:
                    print(f"[DEBUG] スレッド {thread_ts}: {len(replies)}件の返信")

                for reply in replies:
                    process_message(reply, is_thread_reply=True)

            # 次のポーリングまで待機
            time.sleep(polling_interval)

    except KeyboardInterrupt:
        print("\n\nボットを終了します。")
    except Exception as e:
        print(f"\n予期しないエラー: {e}")

if __name__ == "__main__":
    main()
