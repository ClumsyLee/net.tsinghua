var jsdom = require('jsdom');
var fs = require('fs');
var jquery = fs.readFileSync("./jquery.js", "utf-8");
var request = require('request');

BASE_URL = 'http://net.tsinghua.edu.cn';
STATUS_URL = BASE_URL + '/rad_user_info.php';
LOGIN_URL = BASE_URL + '/do_login.php';

exports.auto_login = true;
exports.status = {
  username: null,
  usage: null,
  balance: null
};

// exports.login = function login() {
//   jsdom.env({
//     url: 'http://net.tsinghua.edu.cn/rad_user_info.php',
//     src: [jquery],
//     done: function (err, window) {
//       if (err) {
//         console.log('')
//       }
//       var uname = "lisihan13";
//       var md5_pass = "532da56d5f287fe343ca1eaa3234aa0c";

//       var payload = "action=login&username=" + uname + "&password={MD5_HEX}" + md5_pass +
//           "&ac_id=1";
//       window.$.post("/do_login.php", payload, function(res) {
//         console.log(res);
//       });
//     }
//   });
// }

// Call callback if login successful.
exports.login = function login(username, md5_pass, callback) {
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
      if (body == 'Login is successful.') {
        callback();
      } else if (err) {
        console.error('Error while logging in: %s', err);
      } else {
        console.error('Failed to login: %s', body);
      }
    }
  );
}


function get_status() {
  // body...
}
