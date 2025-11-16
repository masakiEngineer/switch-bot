"""AIエージェントのテストスクリプト"""
from agent import process_user_request
import time

# テストケース（シーリングライトの各種機能）
test_cases = [
    "デバイス一覧を見せて",
    "シーリングライトをつけて",
    "シーリングライトの明るさを50%にして",
    "シーリングライトを暖色にして",
    "シーリングライトを消して",
]

print("=== AIエージェントのテスト ===\n")

for test_input in test_cases:
    print(f"入力: {test_input}")
    try:
        response = process_user_request(test_input)
        print(f"出力: {response}")
    except Exception as e:
        print(f"エラー: {str(e)}")
    print("-" * 50)
    time.sleep(2)  # API制限を考慮して少し待機
