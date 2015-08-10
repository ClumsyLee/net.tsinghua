from PyQt5.QtWidgets import QApplication, QWidget
from ui_settings import Ui_Settings

class Settings(QWidget, Ui_Settings):
    """Settings"""
    def __init__(self, parent=None):
        super(Settings, self).__init__(parent)
        self.setupUi(self)

        self.update_widgets()

    def on_user_list_currentRowChanged(self, current_row):
        """Update infos on the right side"""
        self.update_widgets()

    def clear_infos(self):
        self.name.setText('')
        self.id.setText('')

        self.username.setText('')
        self.password.setText('')

        self.balance.setText('')
        self.ipv4_byte.setText('')
        self.ipv6_byte.setText('')
        self.last_check.setText('')

        self.set_password_editable(True)

    def show_infos(self, acc):
        self.username.setText(acc.username)

        if acc.valid:  # Disable password editing if already valid.
            self.password.setText('*' * 32)  # Just use stars to present it.
            self.set_password_editable(False)

        if acc.last_check:  # We have extra infos to show.
            infos = acc.infos

            self.name.setText(infos['name'])
            self.id.setText(infos['id'])

            self.balance.setText('{balance} 元'.format_map(infos))
            self.ipv4_byte.setText('{ipv4_byte} B'.format_map(infos))
            self.ipv6_byte.setText('{ipv6_byte} B'.format_map(infos))
            self.last_check.setText(str(acc.last_check))
        else:
            self.last_check.setText('从未')

    def update_widgets(self):
        self.clear_infos()

        acc = self.user_list.current_account()
        if acc:
            self.show_infos(acc)
            self.delete_button.setEnabled(True)
        else:
            self.delete_button.setEnabled(False)

    def set_password_editable(self, editable):
        self.password.setEnabled(editable)
        self.md5_check_box.setEnabled(editable)
        # If editable,
        self.md5_check_box.setChecked(not editable)

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    settings = Settings()
    settings.show()

    sys.exit(app.exec_())
