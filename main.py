import sys
import json
import os
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox

# 設定ファイルのパス
SETTINGS_FILE = "settings.json"

class SettingsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_settings()

    def initUI(self):
        self.setWindowTitle("設定入力")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        # 入力項目
        self.fields = {}
        self.labels = {
            "USERNAME": "自身のVRChatユーザー名:",
            "PASSWORD": "自身のVRChatパスワード:",
            "USER_ID_TO_WATCH": "ログインを検知したいユーザーID(usr_xxx):",
            "GMAIL_ADDRESS": "自身のGmailアドレス:",
            "GMAIL_PASSWORD": "自身のGmailパスワード:",
            "TO_EMAIL": "通知先のメールアドレス(自身のGmailアドレスでも可):",
        }

        for key, label_text in self.labels.items():
            label = QLabel(label_text, self)
            layout.addWidget(label)

            line_edit = QLineEdit(self)
            if "PASSWORD" in key:  # パスワードは非表示
                line_edit.setEchoMode(QLineEdit.EchoMode.Password)

            self.fields[key] = line_edit
            layout.addWidget(line_edit)

        # 保存ボタン
        self.save_button = QPushButton("保存", self)
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def load_settings(self):
        """設定ファイルを読み込む"""
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
                settings = json.load(file)
                for key, value in settings.items():
                    if key in self.fields:
                        self.fields[key].setText(value)

    def save_settings(self):
        """設定を保存する"""
        settings = {key: self.fields[key].text() for key in self.fields}

        with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(settings, file, indent=4, ensure_ascii=False)

        QMessageBox.information(self, "保存完了", "設定を保存しました。")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingsApp()
    window.show()
    sys.exit(app.exec())
