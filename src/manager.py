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
        if len(self.accounts):
            acc = self.accounts[0]
            logging.info('Logging in using %s', acc)
            return acc.login()
        else:
            logging.warning('No accounts for logging in, please add some')
            return False

    def logout(self):
        logging.info('Logging out')
        return True   # TODO: Implement.

    def check_all(self):
        for acc in self.accounts:
            acc.check()

    def save(self):
        save_accounts(self.accounts, self.accounts_filename)
