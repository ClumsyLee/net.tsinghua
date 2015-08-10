from PyQt5.QtWidgets import QApplication, QWidget
from ui_settings import Ui_Settings

class Settings(QWidget, Ui_Settings):
    """Settings"""
    def __init__(self, parent=None):
        super(Settings, self).__init__(parent)
        self.setupUi(self)

    def on_user_list_currentRowChanged(self, current_row):
        """Update infos on the right side"""
        if current_row == -1:
            self.clear_infos()
        else:
            self.show_infos(self.user_list.accounts[current_row])

    def clear_infos(self):
        pass

    def show_infos(self, acc):
        infos = acc.infos

        self.name.setText(infos['name'])
        self.id.setText(infos['id'])

        self.username.setText(acc.username)

        self.balance.setText('{balance} 元'.format_map(infos))
        self.ipv4_byte.setText('{ipv4_byte} B'.format_map(infos))
        self.ipv6_byte.setText('{ipv6_byte} B'.format_map(infos))
        if acc.last_check:
            self.last_check.setText(str(acc.last_check))
        else:
            self.last_check.setText('从未')


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    settings = Settings()
    settings.show()
    settings.show_infos(settings.user_list.accounts[0])

    sys.exit(app.exec_())
