var jsdom = require('jsdom');
var fs = require('fs');
var jquery = fs.readFileSync("./jquery.js", "utf-8");

exports.login = function login() {
  jsdom.env({
    url: 'http://net.tsinghua.edu.cn/',
    src: [jquery],
    done: function (err, window) {
      var uname = "lisihan13";
      var md5_pass = "532da56d5f287fe343ca1eaa3234aa0c";

      var payload = "action=login&username=" + uname + "&password={MD5_HEX}" + md5_pass +
          "&ac_id=1";
      window.$.post("/do_login.php", payload, function(res) {
        console.log(res);
      });
    }
  });
}
