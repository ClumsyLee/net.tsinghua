from datetime import datetime
from hashlib import md5
import logging
from re import match, search, DOTALL

from requests.sessions import Session
from bs4 import BeautifulSoup
from keyring import set_password, get_password
import yaml

BASE_URL = 'https://usereg.tsinghua.edu.cn'
LOGIN_PAGE = BASE_URL + '/do.php'
INFO_PAGE = BASE_URL + '/user_info.php'
SERVICE_NAME = 'net.tsinghua'

class Account(object):
    """Tsinghua Account"""
    def __init__(self, username, password, is_md5=False):
        super().__init__()
        self.username = username
        self.password = None
        self.is_md5 = None
        self.set_password(password, is_md5)

        # Account Infomations.
        self.infos = {}
        self.infos['name'] = ''
        self.infos['id'] = ''

        # Balance & Usage.
        self.infos['balance'] = 0
        self.infos['ipv4_byte'] = 0
        self.infos['ipv6_byte'] = 0
        self.last_check = None

        # Whether it is a valid acount.
        self.valid = False

    def set_password(self, password, is_md5=False):
        if is_md5 and len(password) != 32:
            raise ValueError('Invalid MD5ed password ({}): Length should be 32'
                             .format(password))
        self.password = password
        self.is_md5 = is_md5

    @property
    def md5_pass(self):
        password = self.password
        return password if self.md5 else md5(password.encode()).hexdigest()

    def check(self):
        """Try to check the validity & infos of the acount, return True if
        succeeded."""
        logging.info('Checking account, username: %s', self.username)
        try:
            s = Session()
            payload = dict(action='login',
                           user_login_name=self.username,
                           user_password=self.md5_pass)

            login = s.post(LOGIN_PAGE, payload, verify=False)
            if not login:  # Not a normal response, mayby the network is down?
                logging.error('Login request failed: received %s', login)
                return False

            if login.text == 'ok':
                self.__update_infos(s)
                self.valid = True   # Update validity only if infos updated.
            else:
                self.valid = False

            return True
        except Exception as e:  # Things happened so checking did not finish.
            logging.error('Exception received while checking: %s', e)
            return False

    def login(self):
        """Login using current account"""
        return False   # TODO: Implement.

    def __update_infos(self, session):
        # Parse HTML.
        soup = BeautifulSoup(session.get(INFO_PAGE, verify=False).text,
                             'html.parser')
        blocks = map(BeautifulSoup.get_text, soup.select('.maintd'))
        i = map(str.strip, blocks)  # Only works in python 3.
        infos = dict(zip(i, i))

        self.infos['name'] = infos['姓名']
        self.infos['id'] = infos['证件号']

        self.infos['balance'] = _head_float(infos['帐户余额'])
        self.infos['ipv4_byte'] = _head_int(infos['使用流量(IPV4)'])
        self.infos['ipv6_byte'] = _head_int(infos['使用流量(IPV6)'])

        # We don't need microsecond.
        self.last_check = datetime.today().replace(microsecond=0)

    def __repr__(self):
        return '<Account(%s, %s, %sB, ¥%s, %s)>' % (self.username,
                                                    self.valid,
                                                    self.infos['ipv4_byte'],
                                                    self.infos['balance'],
                                                    self.last_check)

def _head_int(s):
    return int(match(r'\d+', s).group())

def _head_float(s):
    return float(match(r'\d+(\.\d+)?', s).group())

# Save / load accounts.
def save_accounts(accounts, filename):
    content = {}
    for acc in accounts:
        # Save password.
        set_password(SERVICE_NAME, acc.username, acc.password)
        # Save infos.
        infos = acc.infos
        infos['is_md5'] = acc.is_md5
        infos['last_check'] = acc.last_check
        infos['valid'] = acc.valid

        content[acc.username] = infos

    yaml.dump(content, open(filename, 'w', encoding='utf-8'),
              default_flow_style=False,
              allow_unicode=True)

def load_accounts(filename):
    accounts = []
    content = yaml.load(open(filename, encoding='utf-8'))

    for username, infos in content.items():
        # Load password.
        password = get_password(SERVICE_NAME, username)
        acc = Account(username, password, infos.pop('is_md5'))
        # Load infos.
        acc.last_check = infos.pop('last_check')
        acc.valid = infos.pop('valid')
        acc.infos = infos

        accounts.append(acc)

    return accounts
