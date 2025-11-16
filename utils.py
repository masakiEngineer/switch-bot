import os
import requests
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# トークンとシークレットを取得
token = os.getenv("SWITCH_BOT_TOKEN")
client_secret = os.getenv("SWITCH_BOT_CLIENT_SECRET")

if not token:
    raise ValueError("SWITCH_BOT_TOKENが.envファイルに設定されていません")

# APIヘッダーを設定
headers = {
    "Authorization": token,
    "Content-Type": "application/json"
}

# デバイス一覧を取得
def get_devices():
    """Switchbotデバイスの一覧を取得"""
    res = requests.get(
        "https://api.switch-bot.com/v1.1/devices",
        headers=headers
    )
    return res.json()

# デバイスステータスを取得
def get_device_status(device_id):
    """デバイスのステータスを取得

    Args:
        device_id: デバイスID
    """
    url = f"https://api.switch-bot.com/v1.1/devices/{device_id}/status"
    res = requests.get(url, headers=headers)
    return res.json()

# デバイスを操作
def control_device(device_id, command, parameter="default"):
    """Switchbotデバイスを操作

    Args:
        device_id: デバイスID
        command: コマンド (例: "turnOn", "turnOff", "press")
        parameter: パラメータ (デフォルト: "default")
    """
    url = f"https://api.switch-bot.com/v1.1/devices/{device_id}/commands"
    data = {
        "command": command,
        "parameter": parameter
    }
    res = requests.post(url, headers=headers, json=data)
    return res.json()

# シーリングライトの明るさを設定
def set_ceiling_light_brightness(device_id, brightness):
    """シーリングライトの明るさを設定

    Args:
        device_id: デバイスID
        brightness: 明るさ (1-100)
    """
    if not 1 <= brightness <= 100:
        raise ValueError("明るさは1-100の範囲で指定してください")

    return control_device(device_id, "setBrightness", str(brightness))

# シーリングライトの色温度を設定
def set_ceiling_light_color_temp(device_id, color_temp):
    """シーリングライトの色温度を設定

    Args:
        device_id: デバイスID
        color_temp: 色温度 (2700-6500K) または "warm"/"cool"などの文字列
    """
    # 文字列指定の場合は数値に変換
    temp_map = {
        "warm": 2700,      # 暖色
        "暖色": 2700,
        "あたたかい": 2700,
        "neutral": 4500,   # 中性
        "昼白色": 4500,
        "cool": 6500,      # 寒色
        "white": 6500,
        "寒色": 6500,
        "白": 6500,
    }

    if isinstance(color_temp, str):
        color_temp = temp_map.get(color_temp.lower(), 4500)

    if not 2700 <= color_temp <= 6500:
        raise ValueError("色温度は2700-6500の範囲で指定してください")

    return control_device(device_id, "setColorTemperature", str(color_temp))

if __name__ == "__main__":
    # デバイス一覧を表示
    devices = get_devices()
    print("=== Switchbotデバイス一覧 ===")
    print(devices)