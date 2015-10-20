var fs = require('fs');
var path = require('path');

var config_path = path.join(
  process.env[(process.platform == 'win32') ? 'USERPROFILE' : 'HOME'],
  '.net.tsinghua.json');

exports.load = function load() {
  console.log('Loading config from %s.', config_path);

  // Default config.
  var config = {
    auto_manage: true,
    auto_manage_interval_msec: 30 * 1000,
    info_update_interval_msec: 5 * 60 * 1000,
    status_update_interval_msec: 60 * 1000,
    auto_update_interval_msec: 24 * 60 * 60 * 1000,
    username: "",
    md5_pass: ""
  };

  try {
    var custom_config = JSON.parse(fs.readFileSync(config_path, "utf-8"));
    for (var attr in custom_config)
      config[attr] = custom_config[attr];
  } catch (err) {
    console.log('Failed to load config: %s', err);
  }

  return config;
}

exports.save = function save(data) {
  console.log('Saving config to %s.', config_path);
  fs.writeFileSync(config_path, JSON.stringify(data, null, 4), "utf-8");
}
