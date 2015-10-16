// Electron modules.
var app = require('app');
var BrowserWindow = require('browser-window');

// 3rd party modules.
var notifier = require('node-notifier');

// Local modules.
var auto_update = require('./auto_update');
var configure = require('./configure');
var net = require('./net');
var usereg = require('./usereg');
var tray = require('./tray');

var config = configure.load();  // Load config before anything else.

// Init auto update.
if (auto_update.init_updater())  // Need to exit now.
  return;

// Status.
var status = 'UNKNOWN';
var last_session = {};

// Account info.
var total_usage = null;
var balance = null;

// Sessions.
var sessions = [];
var last_check = null

function login() {
  console.log('Logging in.');

  net.login(config.username, config.md5_pass, function (err) {
    if (!err) {
      update_all(function () {
        notifier.notify({
          title: '上线成功',
          message: sessions.length.toString() + ' 设备在线\n' + real_time_usage_str()
        });
      });
    }
  });
}

function logout() {
  console.log('Logging out.');

  net.logout(function (err) {
    if (!err) {
      update_all(function () {
        notifier.notify({
          title: '下线成功',
          message: real_time_usage_str()
        });
      });
    }
  });
}

function logout_session(id) {
  console.log('Logging out session %s.', id);

  usereg.logout_session(config.username, config.md5_pass, id, function (err) {
    if (!err)
      update_all();  // Might be current session, so update status as well.
  });
}

function update_status(callback) {
  console.log('Updating status.');

  if (typeof callback === 'undefined') {
    callback = function (err) {};
  }

  net.get_status(function (err, infos) {
    if (err) {
      status = 'ERROR';
    } else {
      if (!infos) {
        status = 'OFFLINE';
      } else {
        if (config.username == infos.username) {
          status = 'ONLINE';

          // These infos belong to current account, save it.
          total_usage = infos.total_usage;
          balance = infos.balance;
        } else {
          status = 'OTHERS_ACCOUNT_ONLINE';
        }
        // Got something useful, update infos.
        last_session.ip = infos.ip;
        last_session.start_time = infos.start_time;
        last_session.usage = infos.usage;
      }
    }
    reset_menu();
    callback(err);
  });
}

function update_infos(callback) {
  console.log('Updating infos using usereg.');

  if (typeof callback === 'undefined') {
    callback = function (err) {};
  }

  usereg.get_infos(config.username, config.md5_pass, function (err, infos) {
    if (err) {
      console.error('Failed to update infos using usereg: %s', err);
    } else {
      total_usage = infos.usage;
      balance = infos.balance;
      sessions = infos.sessions;
      last_check = new Date();  // Record current time.
      reset_menu();
    }
    callback(err);
  });
}

function update_all(callback) {
  update_status(function () {
    update_infos(callback);
  });
}

// Apart from updating data, we need to do some actions when status updated.
function refresh_status() {
  update_status(function () {
    // Try to login if needed.
    if (status == 'OFFLINE' && config.auto_manage && config.username)
      login();
  });
}

// Updating data is all we need.
function refresh_infos() {
  update_infos();
}

// Refresh all.
function refresh() {
  refresh_status();
  refresh_infos();
}

function auto_manage_changed(auto_manage) {
  config.auto_manage = auto_manage;
  configure.save();
}

// FIXME: Looks ugly now.
function account_setting() {
  var dialog = new BrowserWindow({width: 400, height: 220, resizable: true});
  dialog.loadUrl('file://' + __dirname + '/account_setting.html');
  dialog.on('close', function () {
    config = configure.load();
    refresh();
  });
}

function reset_menu() {
  tray.reset_menu({
    username: config.username,
    status: status,
    last_session: last_session,
    total_usage: total_usage,
    balance: balance,
    sessions: sessions,
    last_check: last_check
  });
}

tray.on('login', login);
tray.on('logout', logout);
tray.on('logout_session', logout_session);
tray.on('refresh', refresh);
tray.on('auto_manage_changed', auto_manage_changed);
tray.on('account_setting', account_setting);

app.on('ready', function() {
  // Set clocks.
  setInterval(refresh_status, config.status_update_interval_msec);
  setInterval(refresh_infos, config.info_update_interval_msec);

  // Set tray menu.
  reset_menu();

  // Set notifications.
  notifier.on('click', function (notifierObject, options) {
    if (options.title == '未设置帐号')
      account_setting();
  });

  // Prompt users to set account if they haven't.
  if (!config.username) {
    notifier.notify({
      title: '未设置帐号',
      message: '点击这里设置帐号\n或者稍后右键点击状态栏图标 > 账号设置',
      wait: true
    });
  }

  refresh();  // First shot.
  auto_update.check_updates();  // Check for updates.
});

app.on('window-all-closed', function() {});
