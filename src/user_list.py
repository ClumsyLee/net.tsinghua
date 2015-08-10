from PyQt5.QtWidgets import QListWidget

class UserList(QListWidget):
    """User list"""
    def __init__(self, parent=None):
        super(UserList, self).__init__(parent)

    def add_user(self):
        pass

    def delete_user(self):
        pass
