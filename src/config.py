import yaml
from PyQt5.QtWidgets import QDialog

from ui_config import Ui_AccountSettingDialog

CONFIG_FILENAME = 'config.yml'
DEFAULT_CONFIG = dict(
    auto_manage=True,
    auto_manage_interval_msec=30000,
    info_update_interval_msec=300000,
    status_update_interval_msec=60000,
    username=None
)


def load_config(filename=CONFIG_FILENAME):
    config = DEFAULT_CONFIG.copy()
    config.update(yaml.load(open(filename, encoding='utf-8')))
    return config

def save_config(config, filename=CONFIG_FILENAME):
    yaml.dump(config, open(filename, 'w', encoding='utf-8'),
              default_flow_style=False,
              allow_unicode=True)

def update_config(filename=CONFIG_FILENAME, **kw):
    config = load_config(filename)
    config.update(kw)
    save_config(config, filename)

class AccountSettingDialog(QDialog, Ui_AccountSettingDialog):
    """Account setting dialog"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        username = load_config()['username']
        self.username.setText(username)
        if username:
            self.password.setFocus()
