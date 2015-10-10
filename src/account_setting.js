var fs = require('fs');
var md5 = require('md5');
var config;

exports.get_username = function get_username() {
  config = JSON.parse(fs.readFileSync(__dirname + "/config.json",
                            "utf-8"));
  document.getElementById('username').value = config.username;
}

exports.save_account = function save_account() {
  config.username = document.getElementById('username').value;
  config.md5_pass = md5(document.getElementById('password').value);
  fs.writeFileSync(__dirname + "/config.json", JSON.stringify(config, null, 4), "utf-8");
}
