import logging
from account import Account, save_accounts, load_accounts

class Manager(object):
    """Account & login manager"""
    def __init__(self, accounts_filename):
        super().__init__()
        self.accounts_filename = accounts_filename

        try:
            self.accounts = load_accounts(accounts_filename)
        except Exception as e:
            logging.warning('Exception received when loading accounts from %s: '
                            '%s', accounts_filename, e)
            self.accounts = []

    def login(self):
        """Just using the first account.
        Override this method to have a diffrent behavior."""
        return (len(self.accounts) and self.accounts[0].login())

    def logout(self):
        return False   # TODO: Implement.

    def check_all(self):
        for acc in self.accounts:
            acc.check()

    def save(self):
        save_accounts(self.accounts, self.accounts_filename)
