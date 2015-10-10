var jsdom = require('jsdom');
var fs = require('fs');
var jquery = fs.readFileSync(__dirname + "/jquery.js", "utf-8");
var request = require('request').defaults({jar: true});
var encoding = require('encoding');

var utils = require('./utils');

BASE_URL = 'http://usereg.tsinghua.edu.cn';
LOGIN_URL = BASE_URL + '/do.php';
INFO_URL = BASE_URL + '/user_info.php';
SESSIONS_URL = BASE_URL + '/online_user_ipv4.php';

// Call callback(err, infos).
// infos:
// {
//   usage: ...,
//   balance: ...,
//   sessions: [...]
// }
exports.get_infos = function get_infos(username, md5_pass, callback) {
  if (typeof callback === 'undefined') {
    callback = function (err, infos) {};
  }

  login(username, md5_pass, function (err) {
    if (err) {
      callback(err);
    } else {
      // Logged into usereg, fetch user page.
      request(INFO_URL, function (err, r, info_page) {
        if (err) {
          console.error('Error while fetching user info from usereg: %s', err);
          callback(err);
        } else {
          // User page fetched, fetch sessions page.
          request(SESSIONS_URL, function (err, r, sessions_page) {
            if (err) {
              console.error('Error while fetching sessions from usereg: %s', err);
              callback(err);
            } else {
              // Pages fetched, parse them.
              parse_pages(info_page, sessions_page, callback);
            }
          });
        }
      });
    }
  });
}

// Call callback(err).
function login(username, md5_pass, callback) {
  if (typeof callback === 'undefined') {
    callback = function (err) {};
  }

  request.post({
      url: LOGIN_URL,
      form: {
        action: 'login',
        user_login_name: username,
        user_password: md5_pass
      }
    },
    function (err, r, body) {
      if (err) {
        console.error('Error while logging into usereg: %s', err);
        callback(err);
      } else if (body == 'ok') {
        console.info('Logged into usereg using %s', username);
        callback(null);
      } else {
        console.error('Failed to login to usereg: %s', body);
        callback(body);
      }
    }
  );
}

// Call callback(err, infos).
// TODO: catch errors.
function parse_pages(info_page, sessions_page, callback) {
  if (typeof callback === 'undefined') {
    callback = function (err, infos) {};
  }

  encoding.convert(info_page, 'UTF-8', 'GB2312').toString();
  encoding.convert(sessions_page, 'UTF-8', 'GB2312').toString();

  var infos = {};

  // Parse info page.
  jsdom.env(info_page, function (err, window) {
    if (err) {
      console.error('Error while parsing usereg user page: %s', err);
      callback(err);
      return false;
    } else {
      // Parse data pairs.
      var all_infos = {};
      var data = window.document.getElementsByClassName('maintd');

      for (var i = 1; i < data.length; i += 2)
        all_infos[data[i-1].innerText] = data[i].innerText;

      // FIXME
      infos.usage = Number(/\d+/.exec(all_infos["使用流量(IPV4)"])[0]);
      infos.balance = Number(/\d+\.\d+/.exec(all_infos["帐户余额"])[0]);
    }
  });

  // Parse sessions page.
  jsdom.env(info_page, function (err, window) {
    if (err) {
      console.error('Error while parsing usereg sessions page: %s', err);
      callback(err);
    } else {
      // Parse table rows.
      var ROW_LENGTH = 14;
      infos.sessions = [];
      var data = window.document.getElementsByClassName('maintd');

      for (var i = ROW_LENGTH; i <= data.length - ROW_LENGTH; i += ROW_LENGTH) {
        infos.sessions.push({
          id: data[i].getElementsByTagName('input')[0].value,
          ip: data[i + 1].innerText,
          // Date only accept ISO format here.
          start_time: new Date(data[i + 2].replace(' ', 'T') + '+08:00'),
          usage: utils.parse_usage_str(data[i + 3].innerText),
          device_name: data[i + 11].innerText
        });
      };

      // Done, return infos.
      callback(null, infos);
    }
  });
}
