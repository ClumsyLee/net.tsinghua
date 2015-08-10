class UserList(QListWidget):
    """User list"""
    def __init__(self, parent=None):
        super(UserList, self).__init__(parent)
        self.setupUi(self)
