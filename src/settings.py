from PyQt5.QtWidgets import QApplication, QWidget
from ui_settings import Ui_Settings

class Settings(QWidget, Ui_Settings):
    """Settings"""
    def __init__(self, parent=None):
        super(Settings, self).__init__(parent)
        self.setupUi(self)

        self.update_infos(self.user_list.currentRow())

    def on_user_list_currentRowChanged(self, current_row):
        """Update infos on the right side"""
        self.update_infos(current_row)

    def clear_infos(self):
        pass

    def show_infos(self, acc):
        infos = acc.infos

        self.name.setText(infos['name'])
        self.id.setText(infos['id'])

        self.set_login_info_enabled(not acc.valid)
        self.username.setText(acc.username)
        self.password.setText(acc.md5_pass)
        self.md5_check_box.setChecked = True

        self.balance.setText('{balance} 元'.format_map(infos))
        self.ipv4_byte.setText('{ipv4_byte} B'.format_map(infos))
        self.ipv6_byte.setText('{ipv6_byte} B'.format_map(infos))
        if acc.last_check:
            self.last_check.setText(str(acc.last_check))
        else:
            self.last_check.setText('从未')

    def update_infos(self, current_row):
        if current_row == -1:
            self.clear_infos()
        else:
            self.show_infos(self.user_list[current_row])

    def set_login_info_enabled(self, enabled):
        self.username.setEnabled(enabled)
        self.password.setEnabled(enabled)
        self.md5_check_box.setEnabled(enabled)

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    settings = Settings()
    settings.show()

    sys.exit(app.exec_())
