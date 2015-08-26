from keyring import set_password, get_password, delete_password

class AbstractAccount(object):
    """Represent a general account used for logging in."""
    def __init__(self, username):
        super().__init__()
        self.username = username

        self.balance = None
        self.byte = None
        self.max_byte = None
        self.last_check = None

    @property
    def password(self):
        return get_password(self.service_name(), self.username)

    @password.setter
    def password(self, new_pass):
        set_password(self.service_name(), self.username, new_pass)

    @password.deleter
    def password(self):
        delete_password(self.service_name(), self.username)

    # The following methods need to be re-implemented.
    def service_name(self):
        """The service name used in the keyring"""
        return 'net.tsinghua'

    def update(self):
        """Update infos of the account.
        Return True on success, False otherwise."""
        return False

    def login(self):
        """Return True on success, False otherwise."""
        return False

    @staticmethod
    def logout():
        """Return True on success, False otherwise."""
        return False

    @staticmethod
    def status():
        """Return (username, session_start_byte, session_sec) if logged in,
        None if not.
        Raise ConnectionError if cannot connect to login server."""
        raise ConnectionError()
