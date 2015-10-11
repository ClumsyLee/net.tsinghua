var fs = require('fs');
var path = require('path');

var config_path = path.join(
  process.env[(process.platform == 'win32') ? 'USERPROFILE' : 'HOME'],
  '.net.tsinghua.json');

exports.load = function load() {
  console.log('Loading config from %s.', config_path);

  try {
    return JSON.parse(fs.readFileSync(config_path, "utf-8"));
  } catch (err) {
    console.log('Failed to load config (%s), use default.', err);
    return {
      auto_manage: true,
      auto_manage_interval_msec: 30000,
      info_update_interval_msec: 300000,
      status_update_interval_msec: 60000,
      username: "",
      md5_pass: ""
    };
  }
}

exports.save = function save(data) {
  console.log('Saving config to %s.', config_path);
  fs.writeFileSync(config_path, JSON.stringify(data, null, 4), "utf-8");
}
