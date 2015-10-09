var app = require('app');
var Menu = require('menu');
var Tray = require('tray');
var BrowserWindow = require('browser-window');

var autoUpdater = require('auto-updater');
autoUpdater.on('error', function (event, message) {
  console.log(message);
});
autoUpdater.on('checking-for-update', function () {
  console.log('Checking for update');
});
autoUpdater.on('update-available', function () {
  console.log('Update available');
});
autoUpdater.on('update-not-available', function () {
  console.log('Update not available');
});
autoUpdater.on('update-downloaded', function () {
  console.log('Update downloaded');
});
autoUpdater.setFeedUrl('http://net-tsinghua.herokuapp.com/update/darwin_x64/' + app.getVersion());

var fs = require('fs');
var config = JSON.parse(fs.readFileSync(__dirname + "/config.json", "utf-8"));

var net = require('./net');
var utils = require('./utils')

var status = 'UNKNOWN';
var last_session = {};
var sessions = [];
var last_check = null
var total_usage = null;
var balance = null;

var STATUS_STR = {
  UNKNOWN: '未知状态',
  OFFLINE: '离线',
  ONLINE: '在线',
  OTHERS_ACCOUNT_ONLINE: '他人账号在线',
  ERROR: '网络错误',
  NO_CONNECTION: '无连接'
}

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
      template.push({label: session.device_name, submenu: [
        {label: session.ip, enabled: false},
        {label: utils.time_passed_str(session.start_time) + '上线',
         enabled: false},
        {label: '≥ ' + utils.usage_str(session.usage), enabled: false},
        {label: '下线'}
      ]});
    });
  }
  template.push({label: '上次更新：' + utils.time_passed_str(last_check),
                 enabled: false});

  return template.concat([
    // Actions.
    {type: 'separator'},
    {label: '上线', click: login},
    {label: '下线', click: logout},
    {label: '现在刷新', click: update_status},

    // Config.
    {type: 'separator'},
    {label: '自动管理', type: 'checkbox', checked: config.auto_manage},
    {label: '账号设置...', click: account_setting},

    // About.
    {type: 'separator'},
    {label: '关于 ' + app.getName(), role: 'about'},

    // Quit.
    {type: 'separator'},
    {label: '退出', click: function() {app.quit();}}
  ]);
}

function login() {
  net.login(config.username, config.md5_pass, function (err) {
    if (!err)
      update_status();
  });
}

function logout() {
  net.logout(function (err) {
    if (!err)
      update_status();
  });
}

function reset_menu() {
  if (appIcon) {
    console.log('Reseting menu');
    appIcon.setContextMenu(Menu.buildFromTemplate(get_menu_template()));
  }
}

function update_status() {
  console.log('Updating status');

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
  });
}

function account_setting() {
  var dialog = new BrowserWindow({width: 220, height: 120, resizable: false});
  dialog.loadUrl('file://' + __dirname + '/account_setting.html');
}

setInterval(function () {
  update_status();
  // Try to login if needed.
  if (status == 'OFFLINE' && config.auto_manage && config.username)
    login();
}, config.status_update_interval_msec);

app.on('ready', function() {
  appIcon = new Tray(__dirname + '/tray_icon.png');

  reset_menu();
  appIcon.setToolTip('This is my application.');

  update_status();  // First shot.
  autoUpdater.checkForUpdates();  // Check for updates.
});

app.on('window-all-closed', function() {});
