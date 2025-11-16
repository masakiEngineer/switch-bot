import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from utils import get_devices, control_device, set_ceiling_light_brightness, set_ceiling_light_color_temp
from scheduler import add_schedule, get_schedules, remove_schedule

# 環境変数を読み込む
load_dotenv()

# OpenAIクライアントを初期化
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# デバイスタイプごとの操作コマンドマッピング
DEVICE_COMMANDS = {
    "Smart Lock Ultra": {
        "unlock": "unlock",
        "lock": "lock",
        "開ける": "unlock",
        "ロック解除": "unlock",
        "閉める": "lock",
        "ロック": "lock",
    },
    "Curtain3": {
        "open": "turnOn",
        "close": "turnOff",
        "開ける": "turnOn",
        "閉める": "turnOff",
        "半開き": "setPosition",
    },
    "Plug Mini (JP)": {
        "on": "turnOn",
        "off": "turnOff",
        "オン": "turnOn",
        "オフ": "turnOff",
        "つける": "turnOn",
        "消す": "turnOff",
    },
    "Ceiling Light": {
        "on": "turnOn",
        "off": "turnOff",
        "オン": "turnOn",
        "オフ": "turnOff",
        "つける": "turnOn",
        "消す": "turnOff",
    }
}

def get_device_info():
    """デバイス情報を取得して整形"""
    devices_data = get_devices()
    device_list = []

    if devices_data.get("statusCode") == 100:
        for device in devices_data["body"]["deviceList"]:
            device_list.append({
                "id": device["deviceId"],
                "name": device["deviceName"],
                "type": device["deviceType"]
            })

    return device_list

def find_device_by_name(device_name, devices):
    """デバイス名からデバイスを検索（部分一致）"""
    for device in devices:
        if device_name.lower() in device["name"].lower() or device["name"].lower() in device_name.lower():
            return device
    return None

def execute_device_command(device_id, device_type, action):
    """デバイスコマンドを実行"""
    command_map = DEVICE_COMMANDS.get(device_type, {})
    command = command_map.get(action)

    if not command:
        # デフォルトコマンド
        if action in ["on", "オン", "つける", "開ける"]:
            command = "turnOn"
        elif action in ["off", "オフ", "消す", "閉める"]:
            command = "turnOff"
        else:
            command = action

    result = control_device(device_id, command)
    return result

# Function calling用の関数定義
tools = [
    {
        "type": "function",
        "function": {
            "name": "control_switchbot_device",
            "description": "Switchbotデバイスを操作します。デバイス名と操作内容を指定してください。",
            "parameters": {
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "操作するデバイスの名前（例：カーテン、プラグ、スマートロック、シーリングライト）"
                    },
                    "action": {
                        "type": "string",
                        "description": "実行する操作（例：on, off, open, close, lock, unlock, オン、オフ、開ける、閉める）"
                    }
                },
                "required": ["device_name", "action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_light_brightness",
            "description": "シーリングライトの明るさを調整します。",
            "parameters": {
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "シーリングライトのデバイス名"
                    },
                    "brightness": {
                        "type": "integer",
                        "description": "明るさ（1-100の範囲）。例：50で50%の明るさ"
                    }
                },
                "required": ["device_name", "brightness"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_light_color_temperature",
            "description": "シーリングライトの色温度を調整します。暖色、昼白色、寒色などに変更できます。",
            "parameters": {
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "シーリングライトのデバイス名"
                    },
                    "color_temp": {
                        "type": "string",
                        "description": "色温度。warm/暖色（暖かい色）、neutral/昼白色（中間色）、cool/寒色/白（白い色）のいずれか"
                    }
                },
                "required": ["device_name", "color_temp"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_device_schedule",
            "description": "デバイスを指定時刻に自動操作するスケジュールを追加します。",
            "parameters": {
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "デバイス名（例：シーリングライト、カーテン）"
                    },
                    "time": {
                        "type": "string",
                        "description": "実行時刻（HH:MM形式、例：07:00、19:30）"
                    },
                    "action": {
                        "type": "string",
                        "description": "実行する操作（例：turnOn、turnOff、setBrightness）"
                    },
                    "brightness": {
                        "type": "integer",
                        "description": "明るさ（setBrightnessの場合のみ必要、1-100）"
                    },
                    "color_temp": {
                        "type": "string",
                        "description": "色温度（setColorTemperatureの場合のみ必要）"
                    }
                },
                "required": ["device_name", "time", "action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_schedules",
            "description": "登録されているスケジュールの一覧を取得します。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_device_list",
            "description": "利用可能なSwitchbotデバイスの一覧を取得します。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

def process_user_request(user_input, conversation_history=None):
    """ユーザーのリクエストを処理

    Args:
        user_input: ユーザーの入力
        conversation_history: 会話履歴のリスト（[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]）
    """
    # デバイス情報を取得
    devices = get_device_info()
    device_info_text = "\n".join([f"- {d['name']} ({d['type']})" for d in devices])

    # システムプロンプト
    system_prompt = f"""あなたはSwitchbotデバイスを操作するアシスタントです。
以下のデバイスが利用可能です：

{device_info_text}

重要: 関数を呼び出す際は、上記のデバイスリストから実際のデバイス名を使用してください。
デバイス名は部分一致で検索されますが、できるだけ正確な名前を使ってください。
例：
- ユーザー: 「カーテン」→ device_name: 「カーテン1」または「カーテン」
- ユーザー: 「シーリングライト」→ device_name: 「白いシーリングライト」または「シーリングライト」

シーリングライトには以下の機能があります：
- ON/OFF: つける、消す
- 明るさ調整: 1-100%で指定（例：「明るさを50%に」「半分の明るさに」）
- 色温度調整: 暖色/warm（暖かい色）、昼白色/neutral（中間色）、寒色/cool/白（白い色）

会話履歴を参照して文脈を理解してください。
例：前のメッセージで「シーリングライト」について話していた場合、「暗くして」という指示は「シーリングライトを暗くする」という意味です。
"""

    # OpenAI APIを呼び出し
    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # 会話履歴を追加
    if conversation_history:
        messages.extend(conversation_history)

    # 現在のユーザー入力を追加
    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # コスト効率の良いモデル
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Function callingが呼び出された場合
    if tool_calls:
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            if function_name == "get_device_list":
                return f"利用可能なデバイス:\n{device_info_text}"

            elif function_name == "control_switchbot_device":
                device_name = function_args["device_name"]
                action = function_args["action"]

                # デバイスを検索
                device = find_device_by_name(device_name, devices)

                if not device:
                    return f"エラー: '{device_name}'というデバイスが見つかりません。\n利用可能なデバイス:\n{device_info_text}"

                # デバイスを操作
                result = execute_device_command(device["id"], device["type"], action)

                if result.get("statusCode") == 100:
                    return f"OK: {device['name']}を{action}しました！"
                else:
                    return f"エラー: {device['name']}の操作に失敗しました。\n詳細: {result}"

            elif function_name == "set_light_brightness":
                device_name = function_args["device_name"]
                brightness = function_args["brightness"]

                # デバイスを検索
                device = find_device_by_name(device_name, devices)

                if not device:
                    return f"エラー: '{device_name}'というデバイスが見つかりません。\n利用可能なデバイス:\n{device_info_text}"

                # 明るさを設定
                result = set_ceiling_light_brightness(device["id"], brightness)

                if result.get("statusCode") == 100:
                    return f"OK: {device['name']}の明るさを{brightness}%に設定しました！"
                else:
                    return f"エラー: {device['name']}の明るさ設定に失敗しました。\n詳細: {result}"

            elif function_name == "set_light_color_temperature":
                device_name = function_args["device_name"]
                color_temp = function_args["color_temp"]

                # デバイスを検索
                device = find_device_by_name(device_name, devices)

                if not device:
                    return f"エラー: '{device_name}'というデバイスが見つかりません。\n利用可能なデバイス:\n{device_info_text}"

                # 色温度を設定
                result = set_ceiling_light_color_temp(device["id"], color_temp)

                if result.get("statusCode") == 100:
                    return f"OK: {device['name']}の色温度を{color_temp}に設定しました！"
                else:
                    return f"エラー: {device['name']}の色温度設定に失敗しました。\n詳細: {result}"

            elif function_name == "add_device_schedule":
                device_name = function_args["device_name"]
                time_str = function_args["time"]
                action = function_args["action"]

                # デバイスを検索
                device = find_device_by_name(device_name, devices)

                if not device:
                    return f"エラー: '{device_name}'というデバイスが見つかりません。\n利用可能なデバイス:\n{device_info_text}"

                # パラメータを取得
                params = {}
                if "brightness" in function_args:
                    params["brightness"] = function_args["brightness"]
                if "color_temp" in function_args:
                    params["color_temp"] = function_args["color_temp"]

                # スケジュールを追加
                schedule_item = add_schedule(
                    time_str,
                    device["id"],
                    device["name"],
                    action,
                    **params
                )

                param_text = ""
                if params:
                    param_text = f"（{', '.join([f'{k}={v}' for k, v in params.items()])}）"

                return f"OK: {device['name']}を{time_str}に{action}{param_text}するスケジュールを追加しました！"

            elif function_name == "get_schedules":
                schedule_list = get_schedules()

                if not schedule_list:
                    return "登録されているスケジュールはありません。"

                result_text = "登録済みスケジュール:\n"
                for i, item in enumerate(schedule_list):
                    params_text = ""
                    if item.get("params"):
                        params_text = f" ({', '.join([f'{k}={v}' for k, v in item['params'].items()])})"

                    result_text += f"{i+1}. {item['time']} - {item['device_name']} - {item['action']}{params_text}\n"

                return result_text

    # Function callingが呼び出されなかった場合
    return response_message.content

def main():
    """メインループ"""
    print("=== Switchbot AIエージェント ===")
    print("自然言語でSwitchbotデバイスを操作できます")
    print("例: 'カーテンを開けて', 'プラグをオンにして', 'デバイス一覧を見せて'")
    print("終了するには 'exit' または 'quit' と入力してください\n")

    while True:
        user_input = input("あなた: ").strip()

        if user_input.lower() in ["exit", "quit", "終了"]:
            print("エージェントを終了します。")
            break

        if not user_input:
            continue

        try:
            response = process_user_request(user_input)
            print(f"エージェント: {response}\n")
        except Exception as e:
            print(f"エラーが発生しました: {str(e)}\n")

if __name__ == "__main__":
    main()
