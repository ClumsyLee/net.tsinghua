import yaml
from PyQt5.QtWidgets import QDialog

from ui_config import Ui_AccountSettingDialog

CONFIG_FILENAME = 'config.yml'

def load_config(filename=CONFIG_FILENAME):
    return yaml.load(open(filename, encoding='utf-8'))

def save_config(config, filename=CONFIG_FILENAME):
    yaml.dump(config, open(filename, 'w', encoding='utf-8'),
              default_flow_style=False,
              allow_unicode=True)

class AccountSettingDialog(QDialog, Ui_AccountSettingDialog):
    """Account setting dialog"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        username = load_config()['username']
        self.username.setText(username)
        if username:
            self.password.setFocus()
