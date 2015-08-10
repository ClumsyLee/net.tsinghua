from PyQt5.QtWidgets import QApplication, QWidget
from ui_settings import Ui_Settings

class Settings(QWidget, Ui_Settings):
    """Settings"""
    def __init__(self, parent=None):
        super(Settings, self).__init__(parent)
        self.setupUi(self)

        self.update_infos()

    def on_user_list_currentRowChanged(self, current_row):
        """Update infos on the right side"""
        self.update_infos()

    def on_username_textEdited(self, text):
        # Refuse to check if username is empty.
        self.check_now_button.setEnabled(len(text))
        self.user_list.current_account().username = text
        # TODO: Only write to account when editing finished.
        self.user_list.update_current_row()

    def clear_infos(self):
        self.name.setText('')
        self.id.setText('')

        self.username.setText('')
        self.password.setText('')
        self.md5_check_box.setChecked(False)
        self.set_login_info_enabled(True)

        self.balance.setText('')
        self.ipv4_byte.setText('')
        self.ipv6_byte.setText('')
        self.last_check.setText('')

    def show_infos(self, acc):
        self.set_login_info_enabled(not acc.valid)
        self.username.setText(acc.username)
        if acc.valid:
            self.password.setText(acc.md5_pass)
            self.md5_check_box.setChecked(True)
            self.set_login_info_enabled(False)

        if acc.last_check:  # We have some infos to show.
            infos = acc.infos

            self.name.setText(infos['name'])
            self.id.setText(infos['id'])

            self.balance.setText('{balance} 元'.format_map(infos))
            self.ipv4_byte.setText('{ipv4_byte} B'.format_map(infos))
            self.ipv6_byte.setText('{ipv6_byte} B'.format_map(infos))
            self.last_check.setText(str(acc.last_check))
        else:
            self.last_check.setText('从未')

    def update_infos(self):
        self.clear_infos()

        current_row = self.user_list.currentRow()
        if current_row >= 0:
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
