"""Switchbotデバイスのスケジュール管理"""
import os
import time
import schedule
import json
from datetime import datetime
from dotenv import load_dotenv
from utils import get_devices, control_device, set_ceiling_light_brightness, set_ceiling_light_color_temp

# 環境変数を読み込む
load_dotenv()

# スケジュールを保存するファイル
SCHEDULE_FILE = "schedules.json"

# スケジュール一覧
schedules = []

def load_schedules():
    """スケジュールをファイルから読み込み"""
    global schedules
    try:
        if os.path.exists(SCHEDULE_FILE):
            with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
                schedules = json.load(f)
            print(f"スケジュールを読み込みました: {len(schedules)}件")
        else:
            schedules = []
    except Exception as e:
        print(f"スケジュール読み込みエラー: {e}")
        schedules = []

def save_schedules():
    """スケジュールをファイルに保存"""
    try:
        with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
            json.dump(schedules, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"スケジュール保存エラー: {e}")

def add_schedule(time_str, device_id, device_name, action, **kwargs):
    """スケジュールを追加

    Args:
        time_str: 時刻 (例: "07:00", "19:30")
        device_id: デバイスID
        device_name: デバイス名
        action: 実行する操作 (例: "turnOn", "setBrightness")
        **kwargs: 追加パラメータ (brightness, color_temp など)
    """
    schedule_item = {
        "time": time_str,
        "device_id": device_id,
        "device_name": device_name,
        "action": action,
        "params": kwargs
    }

    schedules.append(schedule_item)
    save_schedules()

    # scheduleライブラリに登録
    register_schedule(schedule_item)

    return schedule_item

def register_schedule(schedule_item):
    """スケジュールをscheduleライブラリに登録"""
    time_str = schedule_item["time"]
    device_id = schedule_item["device_id"]
    device_name = schedule_item["device_name"]
    action = schedule_item["action"]
    params = schedule_item.get("params", {})

    def job():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] スケジュール実行: {device_name} - {action}")

        if action == "setBrightness":
            brightness = params.get("brightness", 100)
            result = set_ceiling_light_brightness(device_id, brightness)
        elif action == "setColorTemperature":
            color_temp = params.get("color_temp", "neutral")
            result = set_ceiling_light_color_temp(device_id, color_temp)
        else:
            parameter = params.get("parameter", "default")
            result = control_device(device_id, action, parameter)

        if result.get("statusCode") == 100:
            print(f"  → 成功: {device_name}を{action}しました")
        else:
            print(f"  → 失敗: {result}")

    schedule.every().day.at(time_str).do(job)
    print(f"スケジュール登録: {time_str} - {device_name} - {action}")

def get_schedules():
    """スケジュール一覧を取得"""
    return schedules

def remove_schedule(index):
    """スケジュールを削除

    Args:
        index: 削除するスケジュールのインデックス
    """
    if 0 <= index < len(schedules):
        removed = schedules.pop(index)
        save_schedules()

        # scheduleライブラリからも削除（全てクリアして再登録）
        schedule.clear()
        for item in schedules:
            register_schedule(item)

        return removed
    return None

def clear_all_schedules():
    """全てのスケジュールを削除"""
    global schedules
    schedules = []
    save_schedules()
    schedule.clear()

def run_scheduler():
    """スケジューラーを実行（無限ループ）"""
    load_schedules()

    # 既存のスケジュールを登録
    for item in schedules:
        register_schedule(item)

    print("スケジューラーを起動しました")
    print(f"登録済みスケジュール: {len(schedules)}件")

    while True:
        schedule.run_pending()
        time.sleep(10)  # 10秒ごとにチェック

if __name__ == "__main__":
    # テスト用
    print("=== Switchbotスケジューラー ===")
    run_scheduler()
