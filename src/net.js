var jsdom = require('jsdom');
var request = require('request');

BASE_URL = 'http://net.tsinghua.edu.cn';
STATUS_URL = BASE_URL + '/rad_user_info.php';
LOGIN_URL = BASE_URL + '/do_login.php';

// Call callback(err).
exports.login = function login(username, md5_pass, callback) {
  if (typeof callback === 'undefined') {
    callback = function (err) {};
  }

  request.post({
      url: LOGIN_URL,
      form: {
        action: 'login',
        username: username,
        password: '{MD5_HEX}' + md5_pass,
        ac_id: 1
      }
    },
    function (err, r, body) {
      if (err) {
        console.error('Error while logging in: %s', err);
        callback(err);
      } else if (body == 'Login is successful.') {
        console.info('Logged in using %s', username);
        callback(null);
      } else {
        console.error('Failed to login: %s', body);
        callback(body);
      }
    }
  );
}

// Call callback(err).
exports.logout = function logout(callback) {
  // FIXME: Ugly, use || or something to fix it?
  if (typeof callback === 'undefined') {
    callback = function (err) {};
  }

  request.post({
      url: LOGIN_URL,
      form: {
        action: 'logout'
      }
    },
    function (err, r, body) {
      if (err) {
        console.error('Error while logging out: %s', err);
        callback(err);
      } else {
        console.info('Logged out');
        callback(null);
      }
    }
  );
}

// Call callback(err, infos).
exports.get_status = function get_status(callback) {
  if (typeof callback === 'undefined') {
    callback = function (err, infos) {};
  }

  request(STATUS_URL, function (err, r, body) {
    if (err) {
      console.error('Error while getting status: %s', err);
      callback(err);
    } else {
      var infos;
      if (body) {
        var info_strs = body.split(',');
        infos = {
          username: info_strs[0],
          start_time: new Date(Number(info_strs[1]) * 1000),
          usage: Number(info_strs[3]),
          total_usage: Number(info_strs[6]),
          ip: info_strs[8],
          balance: Number(info_strs[11])
        };
      } else {
        infos = null;
      }
      console.log('Got status: %s', JSON.stringify(infos));
      callback(null, infos);
    }
  });
}
