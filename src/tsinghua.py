from copy import deepcopy
from datetime import datetime
from hashlib import md5
import logging
from re import match

from bs4 import BeautifulSoup
from requests import get, post, Session as _Session, RequestException
from keyring import set_password, get_password, delete_password
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtNetwork import QNetworkConfigurationManager

def _head_int(s):
    return int(match(r'\d+', s).group())

def _head_float(s):
    return float(match(r'\d+(\.\d+)?', s).group())

def _usage_to_byte(usage):
    num, unit = float(usage[:-1]), usage[-1].upper()

    if unit == 'B':
        ratio = 1
    elif unit == 'K':
        ratio = 1000
    elif unit == 'M':
        ratio = 1000000
    elif unit == 'G':
        ratio = 1000000000
    else:
        raise ValueError('Unknown unit: ' + unit)

    return int(num * ratio)

class Session(object):
    """Session"""
    def __init__(self, username, session_id=None, ip=None, start_time=None,
                 byte=None, device_name='UNKNOWN'):
        super().__init__()

        self.username = username
        self.session_id = session_id
        self.ip = ip
        self.start_time = start_time
        self.byte = byte
        self.device_name = device_name

    def __repr__(self):
        return 'Session({}, {}, {}, {}, {}, {})'.format(self.username,
                                                        self.session_id,
                                                        self.ip,
                                                        self.start_time,
                                                        self.byte,
                                                        self.device_name)

    def logout(self):
        if self.session_id is None:
            r = post(Account.LOGIN_PAGE, data={'action': 'logout'})
            if r.text != 'Logout is successful.':
                raise ConnectionError('Failed to logout current session: {}({})'
                                      .format(r, r.text))
        else:
            Usereg(self.username).logout_session(self.session_id)


class Usereg(object):
    """usereg.tsinghua.edu.cn"""
    BASE_URL = 'https://usereg.tsinghua.edu.cn'
    LOGIN_PAGE = BASE_URL + '/do.php'
    INFO_PAGE = BASE_URL + '/user_info.php'
    SESSIONS_PAGE = BASE_URL + '/online_user_ipv4.php'

    def __init__(self, username):
        super().__init__()
        self.username = username
        self._s = self.login()

    def login(self):
        """Use the current account to login to usereg and return the session.
        Raise ConnectionError if on fails."""
        acc = Account(self.username)
        try:
            if not acc.username:  # Empty username.
                raise ConnectionError('Username not set')

            s = _Session()
            payload = dict(action='login',
                           user_login_name=acc.username,
                           user_password=acc.md5_pass)
            r = s.post(self.LOGIN_PAGE, payload, verify=False)
            r.raise_for_status()

            if r.text == 'ok':
                return s
            else:
                raise ConnectionError(r.text)

        except (RequestException, ConnectionError) as e:
            raise ConnectionError('Failed to login to usereg: {}'.format(e))

    def account_info(self):
        """Fetch infos from info page, return a dict containing infos"""
        try:
            r = self._s.get(self.INFO_PAGE, verify=False)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')

            blocks = map(BeautifulSoup.get_text, soup.select('.maintd'))
            i = map(str.strip, blocks)  # Only works in python 3.
            infos = dict(zip(i, i))

            return dict(balance=_head_float(infos['帐户余额']),
                        byte=_head_int(infos['使用流量(IPV4)']))
        except RequestException as e:
            raise ConnectionError('Failed to fetch info page: {}'.format(e))
        except Exception as e:
            raise ValueError('Failed to parse info page: {}'.format(e))

    def sessions(self):
        """Fetch sessions from sessions page, return a list of sessions"""
        try:
            r = self._s.get(self.SESSIONS_PAGE, verify=False)
            r.raise_for_status()

            soup = BeautifulSoup(r.text, 'html.parser')
            table = soup.select('.maintd')

            ROW_LENGTH = 14
            if len(table) % ROW_LENGTH != 0:
                raise ValueError('Unexpected table content: {}'.format(table))

            # Parse sessions.
            sessions = []
            index = ROW_LENGTH
            while index < len(table):
                sessions.append(Session(
                    username=self.username,
                    session_id=table[index].select_one('input')['value'],
                    ip=table[index + 1].text,
                    start_time=datetime.strptime(table[index + 2].text,
                                                 '%Y-%m-%d %H:%M:%S'),
                    byte=_usage_to_byte(table[index + 3].text),
                    device_name=table[index + 11].text))
                index += ROW_LENGTH

            return sessions
        except RequestException as e:
            raise ConnectionError('Failed to fetch sessions page: {}'.format(e))
        except Exception as e:
            raise ValueError('Failed to parse sessions page: {}'.format(e))

    def logout_session(self, session_id):
        try:
            payload = dict(action='drop',
                           user_ip=session_id)
            r = self._s.post(self.SESSIONS_PAGE, payload, verify=False)
            r.raise_for_status()

            if r.text != 'ok':
                raise ConnectionError(r.text)

        except (RequestException, ConnectionError) as e:
            raise ConnectionError('Failed to logout session {}: {}'
                                  .format(session_id, e))


class Account(QObject):
    """Tsinghua account.
    Statuses:
        OFFLINE
        ONLINE
        OTHERS_ACCOUNT_ONLINE
        ERROR
        NO_CONNECTION (No POST/GET attemps will be made)"""
    SERVICE_NAME = 'net.tsinghua'

    BASE_URL = 'https://net.tsinghua.edu.cn'
    STATUS_PAGE = BASE_URL + '/rad_user_info.php'
    LOGIN_PAGE = BASE_URL + '/do_login.php'

    status_changed = pyqtSignal(str)
    info_updated = pyqtSignal(float, int)  # Balance, byte.
    current_session_updated = pyqtSignal(Session)
    sessions_updated = pyqtSignal(list)

    self.network_manager = QNetworkConfigurationManager(self)

    def __init__(self, username):
        super().__init__()
        self.username = username

        self._status = 'NO_CONNECTION'

        self.last_session = None
        self.sessions = []

        self.balance = None
        self.byte = None

    def __str__(self):
        return ('Tsinghua account {}: {}\n'
                '  last_session: {}\n'
                '  sessions: {}\n'
                '  balance: {}\n'
                '  byte: {}').format(self.username, self.status,
                                     self.last_session,
                                     self.sessions,
                                     date_str,
                                     self.balance,
                                     self.byte)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new_status):
        if self._status != new_status:
            self._status = new_status
            self.status_changed.emit(self._status)

    @property
    def password(self):
        return get_password(self.SERVICE_NAME, self.username)

    @password.setter
    def password(self, new_pass):
        set_password(self.SERVICE_NAME, self.username, new_pass)

    @password.deleter
    def password(self):
        delete_password(self.SERVICE_NAME, self.username)

    @property
    def md5_pass(self):
        password = self.password
        if password is None:
            password = ''
        return md5(password.encode()).hexdigest()

    @property
    def max_byte(self):
        if self.balance is None or self.byte is None:
            return None

        return 0  # TODO: Implement.

    @property
    def realtime_byte(self):
        real = self.byte
        for session in self.sessions:
            real += session.byte
        return real

    def setup(self):
        self.network_manager.onlineStateChanged.connect(online_state_changed)
        online_state_changed(self.network_manager.isOnline())  # First shot.

    def update_status(self):
        if self.status == 'NO_CONNECTION':
            return

        try:
            r = get(self.STATUS_PAGE)
            r.raise_for_status

            if not r.text:
                self.status = 'OFFLINE'
            else:
                try:
                    infos = r.text.split(',')
                    username = infos[0]
                    start_time = datetime.fromtimestamp(int(infos[1]))
                    byte = int(infos[3])
                    total_byte = int(infos[6])
                    ip = infos[8]
                    balance = float(infos[11])
                except Exception as e:
                    raise ValueError('Failed to parse status ({}): {}'
                                     .format(r.text, e))

                self.last_session = Session(
                    username=username,
                    ip=ip,
                    start_time=start_time,
                    byte=byte)
                self.current_session_updated.emit(deepcopy(self.last_session))

                if username == self.username:
                    self.status = 'ONLINE'
                    self.balance = balance  # Self online, update account infos.
                    self.byte = total_byte
                    self.info_updated.emit(self.balance, self.byte)
                else:
                    self.status = 'OTHERS_ACCOUNT_ONLINE'

        except (RequestException, ValueError) as e:
            logging.error('Failed to update status: %s', e)
            self.status = 'ERROR'

    def update_infos(self):
        if self.status == 'NO_CONNECTION':
            return

        try:
            usereg = Usereg(self.username)
            sessions = usereg.sessions()
            infos = usereg.account_info()

            self.sessions = sessions
            self.sessions_updated.emit(deepcopy(self.sessions))

            self.balance = infos['balance']
            self.byte = infos['byte']
            self.info_updated.emit(self.balance, self.byte)

        except (ConnectionError, ValueError) as e:
            logging.error('Failed to update account info: %s', e)

    def online_state_changed(self, new_state):
        if not new_state:                     # Go offline.
            self.status = 'NO_CONNECTION'
        elif self.status == 'NO_CONNECTION':  # Go online.
            self.update_status()

    def login(self):
        if self.status == 'NO_CONNECTION':
            return

        if self.username:
            try:
                payload = dict(action='login',
                               username=self.username,
                               password='{MD5_HEX}'+self.md5_pass,
                               ac_id=1)
                r = post(self.LOGIN_PAGE, payload)
                if r.text in ('Login is successful.',
                              'IP has been online, please logout.'):
                    self.update_status()

            except RequestException as e:
                logging.error('Failed to login: %s', e)

    def logout(self):
        if self.status == 'NO_CONNECTION':
            return

        if self.last_session is not None:
            try:
                self.last_session.logout()
                self.update_status()
            except ConnectionError as e:
                logging.error('Failed to logout: %s', e)
