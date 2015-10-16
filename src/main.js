// Built-in modules.
var path = require('path');

// Electron modules.
var app = require('app');
var BrowserWindow = require('browser-window');
var Menu = require('menu');
var shell = require('shell');
var Tray = require('tray');

// 3rd party modules.
var notifier = require('node-notifier');

// Local modules.
var auto_update = require('./auto_update');
var configure = require('./configure');
var net = require('./net');
var usereg = require('./usereg');
var utils = require('./utils');

var config = configure.load();  // Load config before anything else.

// Init auto update.
if (auto_update.init_updater())
  return;

app.dock.hide()  // Hide dock icon as soon as possible.

// Status.
var status = 'UNKNOWN';
var STATUS_STR = {
  UNKNOWN: '未知状态',
  OFFLINE: '离线',
  ONLINE: '在线',
  OTHERS_ACCOUNT_ONLINE: '他人账号在线',
  ERROR: '网络错误',
  NO_CONNECTION: '无连接'
};
var last_session = {};

// Account info.
var total_usage = null;
var balance = null;

// Sessions.
var sessions = [];
var last_check = null


var appIcon = null;

function get_menu_template() {
  var template = [];

  // Status.
  var status_str = STATUS_STR[status];
  // Show session usage if possible.
  if ((status == 'ONLINE' || status == 'OTHERS_ACCOUNT_ONLINE') && last_session)
    status_str = status_str + ' - ' + utils.usage_str(last_session.usage);
  template.push({label: status_str, enabled: false});

  // Account info.
  template.push({type: 'separator'});
  if (!config.username) {
    template.push({label: '未设置帐号', enabled: false});
  } else {
    template.push({label: config.username, enabled: false});
    template.push({label: '本月流量：' + utils.usage_str(total_usage),
                   enabled: false});
    template.push({label: '当前余额：' + utils.balance_str(balance),
                   enabled: false});
  }

  // Sessions.
  template.push({type: 'separator'});
  if (sessions.length == 0) {
    template.push({label: '无设备在线', enabled: false});
  } else {
    template.push({label: '当前在线', enabled: false});

    sessions.forEach(function (session) {
      var label = session.device_name;
      if (session.ip == last_session.ip)  // Current session.
        label += '（本机）';
      template.push({label: label, submenu: [
        {label: session.ip, enabled: false},
        {label: utils.time_passed_str(session.start_time) + '上线',
         enabled: false},
        {label: '≥ ' + utils.usage_str(session.usage), enabled: false},
        {label: '下线', click: function () { logout_session(session.id); }}
      ]});
    });
  }
  // FIXME: Currently it seems there's not menu.aboutToShow.
  // So time will be valid only when status_update_interval_msec < 60s.
  template.push({label: '上次更新：' + utils.time_passed_str(last_check),
                 enabled: false});

  return template.concat([
    // Actions.
    {type: 'separator'},
    {label: '上线', click: login},
    {label: '下线', click: logout},
    {label: '现在刷新', click: refresh},

    // Config.
    {type: 'separator'},
    {label: '自动管理', type: 'checkbox', checked: config.auto_manage,
     click: function () {
      console.log('Auto manage: %s => %s', config.auto_manage, !config.auto_manage);
      config.auto_manage = !config.auto_manage;
      configure.save(config);
    }},
    {label: '账号设置...', click: account_setting},

    // About.
    {type: 'separator'},
    {label: '关于 ' + app.getName(), click: function () {
      shell.openExternal('https://github.com/ThomasLee969/net.tsinghua');
    }},

    // Quit.
    {type: 'separator'},
    {label: '退出', click: function() { app.quit(); }}
  ]);
}

function real_time_usage_str() {
  var real_time_usage = total_usage;
  sessions.forEach(function (session) { real_time_usage += session.usage; });
  return '本月已用 ' + utils.usage_str(real_time_usage) + '（实时）';
}

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

// FIXME: This will close the menu if it is already open.
function reset_menu() {
  if (appIcon) {
    console.log('Reseting menu.');
    appIcon.setContextMenu(Menu.buildFromTemplate(get_menu_template()));

    appIcon.setToolTip(STATUS_STR[status] + ' - ' + real_time_usage_str());
  }
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

// FIXME: Looks ugly now.
function account_setting() {
  var dialog = new BrowserWindow({width: 400, height: 220, resizable: true});
  dialog.loadUrl('file://' + __dirname + '/account_setting.html');
  dialog.on('close', function () {
    config = configure.load();
    refresh();
  });
}

app.on('ready', function() {
  // Set clocks.
  setInterval(refresh_status, config.status_update_interval_msec);
  setInterval(refresh_infos, config.info_update_interval_msec);

  // Set tray icon.
  if (process.platform == 'darwin') {
    appIcon = new Tray(path.join(__dirname, '../resource/tray_icon_Template.png'));
    appIcon.setPressedImage(path.join(__dirname, '../resource/tray_icon_inversed.png'));
  } else {
    appIcon = new Tray(path.join(__dirname, '../resource/tray_icon.png'));
  }

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

  auto_update.check_updates();
});

app.on('window-all-closed', function() {});
