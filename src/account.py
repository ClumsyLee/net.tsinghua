from datetime import datetime
from hashlib import md5
from re import match, search, DOTALL

from requests.sessions import Session
from bs4 import BeautifulSoup

BASE_URL = 'https://usereg.tsinghua.edu.cn'
LOGIN_PAGE = BASE_URL + '/do.php'
INFO_PAGE = BASE_URL + '/user_info.php'

class Account(object):
    """Tsinghua Account"""
    def __init__(self, username, password, is_md5=False):
        super(Account, self).__init__()
        self.username = username

        if is_md5:
            if len(password) != 32:
                raise ValueError('Length of a MD5 string must be 32')
            self.md5_pass = password
        else:
            self.md5_pass = md5(password.encode()).hexdigest()

        # Account Infomations.
        self.name = ''
        self.id = ''

        # Balance & Usage.
        self.balance = 0
        self.ipv4_byte = 0
        self.ipv6_byte = 0
        self.last_check = None

        # Whether it is a valid acount.
        self.valid = False

    def check(self):
        """Try to check the validity & infos of the acount, return True if
        succeeded."""
        try:
            s = Session()
            payload = dict(action='login',
                           user_login_name=self.username,
                           user_password=self.md5_pass)

            login = s.post(LOGIN_PAGE, payload)
            if not login:  # Not a normal response, mayby the server is down?
                return False

            if login.text == 'ok':
                self.update_infos(s)
                self.valid = True   # Update validity only if infos updated.
            else:
                self.valid = False

            return True
        except:  # Things happened so checking did not finish.
            return False

    def update_infos(self, session):
        # Parse HTML.
        soup = BeautifulSoup(session.get(INFO_PAGE).text, 'html.parser')
        blocks = map(BeautifulSoup.get_text, soup.select('.maintd'))
        i = map(str.strip, blocks)  # Only works in python 3.
        infos = dict(zip(i, i))

        self.name = infos['姓名']
        self.id = infos['证件号']

        self.balance = _head_float(infos['帐户余额'])
        self.ipv4_byte = _head_int(infos['使用流量(IPV4)'])
        self.ipv6_byte = _head_int(infos['使用流量(IPV6)'])

        self.last_check = datetime.today()

    def __repr__(self):
        return '<Account(%s, %s, %sB, ¥%s, %s)>' % (self.username,
                                                    self.valid,
                                                    self.ipv4_byte,
                                                    self.balance,
                                                    self.last_check)

def _head_int(s):
    return int(match(r'\d+', s).group())

def _head_float(s):
    return float(match(r'\d+(\.\d+)?', s).group())

if __name__ == '__main__':
    acc = Account('lisihan13', '532da56d5f287fe343ca1eaa3234aa0c', True)
    acc.check()
    print(acc)
