from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QDialog, QInputDialog, QDialogButtonBox
from ui_settings import Ui_Settings
import account

class Settings(QDialog, Ui_Settings):
    """Settings"""
    def __init__(self, parent=None):
        super(Settings, self).__init__(parent)
        self.setupUi(self)
        self.update_widgets()

        self.apply_button = self.buttonBox.button(QDialogButtonBox.Apply)
        self.apply_button.setEnabled(False)
        self.user_list.dirty_changed.connect(self.apply_button.setEnabled)
        self.apply_button.clicked.connect(self.user_list.save)
        self.accepted.connect(self.user_list.save)

    def on_user_list_currentRowChanged(self, current_row):
        """Update infos on the right side"""
        self.update_widgets()

    def on_new_account_returnPressed(self):
        if self.user_list.add_account(self.new_account.text()):
            self.new_account.clear()
            self.password.setFocus(Qt.OtherFocusReason)
        else:
            self.new_account.selectAll()

    def on_password_editingFinished(self):
        """Save password into the account when finish editing."""
        self.user_list.set_password(self.password.text(),
                                    self.md5_check_box.isChecked())

    # @pyqtSlot()
    # def on_check_now_button_clicked(self):

    def keyPressEvent(self, event):
        """Do not handle enter/return key if the user is editing"""
        key = event.key()
        if not ((key == Qt.Key_Enter or key == Qt.Key_Return) and
                (self.new_account.hasFocus() or self.password.hasFocus())):
            super().keyPressEvent(event)

    def clear_infos(self):
        self.name.setText('')
        self.id.setText('')

        self.username.setText('')
        self.password.setText('')
        self.md5_check_box.setChecked(False)

        self.balance.setText('')
        self.ipv4_byte.setText('')
        self.ipv6_byte.setText('')
        self.last_check.setText('')

        self.set_password_editable(False)

    def show_infos(self, acc):
        self.username.setText(acc.username)

        if acc.valid:  # Disable password editing if already valid.
            self.password.setText('*' * 32)  # Just use stars to present it.
            self.md5_check_box.setChecked(True)
        else:
            self.set_password_editable(True)

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
            self.check_now_button.setEnabled(True)
        else:  # Nothing selected.
            self.delete_button.setEnabled(False)
            self.check_now_button.setEnabled(False)

    def set_password_editable(self, editable):
        self.password.setEnabled(editable)
        self.md5_check_box.setEnabled(editable)

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    settings = Settings()
    settings.show()

    sys.exit(app.exec_())
