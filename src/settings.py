from PyQt5.QtWidgets import QApplication, QWidget
from ui_settings import Ui_Settings

class Settings(QWidget, Ui_Settings):
    """Settings"""
    def __init__(self, parent=None):
        super(Settings, self).__init__(parent)
        self.setupUi(self)

    def on_user_list_currentRowChanged(self, current_row):
        print(current_row)

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    settings = Settings()
    settings.show()

    sys.exit(app.exec_())
