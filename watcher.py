import time
import sys
import json
import smtplib
import vrchatapi
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from vrchatapi.api import authentication_api, users_api
from vrchatapi.exceptions import UnauthorizedException
from vrchatapi.models.two_factor_auth_code import TwoFactorAuthCode
from vrchatapi.models.two_factor_email_code import TwoFactorEmailCode

SETTINGS_FILE = "settings.json"

def load_settings():
    """settings.json を読み込む"""
    with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

def send_email(to_email, subject, body, gmail_address, gmail_password):
    """Gmailで通知メールを送信"""
    msg = MIMEMultipart()
    msg["From"] = gmail_address
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(gmail_address, gmail_password)
        server.sendmail(gmail_address, to_email, msg.as_string())
        server.quit()
        print("✅ 通知メールを送信しました！")
    except Exception as e:
        print(f"⚠️ メール送信失敗: {e}")

def monitor_vrchat():
    """VRChat APIを使ってユーザーの状態を監視"""
    settings = load_settings()

    # VRChat API 認証
    config = vrchatapi.Configuration(
        username=settings["USERNAME"],
        password=settings["PASSWORD"]
    )
    api_client = vrchatapi.ApiClient(config)
    
    # User-Agentを設定
    api_client.user_agent = f"VRChatWatcher/1.0 {settings["USERNAME"]}"
    
    auth_api = authentication_api.AuthenticationApi(api_client)
    
    try:
        auth_api.get_current_user()  # 認証確認
        print("✅ VRChat にログイン成功！")
    except UnauthorizedException as e:
            if e.status == 200:
                auth_api.verify2_fa_email_code(two_factor_email_code=TwoFactorEmailCode(input("Email 2FA Code: ")))
            elif "2 Factor Authentication" in e.reason:
                auth_api.verify2_fa(two_factor_auth_code=TwoFactorAuthCode(input("2FA Code: ")))
            else:
                print("API認証エラー: ", e)
                sys.exit(1)
    except vrchatapi.ApiException as e:
        print(f"⚠️ VRChat ログイン失敗: {e}")
        return

    user_api = users_api.UsersApi(api_client)
    user_id = settings["USER_ID_TO_WATCH"]
    prev_status = None  # 前回のステータス

    while True:
        try:
            user = user_api.get_user(user_id=user_id)
            status = user.status
            state = user.state
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]🔍 ウォッチング中: {user.display_name} ({state})")

            # offline → active になったら通知
            if state == "online" and prev_state == "offline":
                send_email(
                    settings["TO_EMAIL"],
                    f"VRChat {user.display_name} がログインしました！",
                    f"{user.display_name} が VRChat にログインしました。",
                    settings["GMAIL_ADDRESS"],
                    settings["GMAIL_PASSWORD"]
                )

            prev_state = state
        except Exception as e:
            print(f"⚠️ ユーザー情報取得エラー: {e}")

        time.sleep(120)  # 2分待機

if __name__ == "__main__":
    monitor_vrchat()
