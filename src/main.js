var app = require('app');
var Menu = require('menu');
var Tray = require('tray');
var BrowserWindow = require('browser-window');
var shell = require('shell');
var cp = require('child_process');

// Load config.
var fs = require('fs');
var config = {};
var path = require('path');

var net = require('./net');
var usereg = require('./usereg');
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

// Config auto update.
var checkForUpdates = function () {};

if (process.platform == 'darwin') {
  // Auto updater for Darwin.
  var autoUpdater = require('auto-updater');
  autoUpdater.on('error', function (event, message) {
    console.log(message);
  });
  autoUpdater.on('checking-for-update', function () {
    console.log('Checking for update.');
  });
  autoUpdater.on('update-available', function () {
    console.log('Update available.');
  });
  autoUpdater.on('update-not-available', function () {
    console.log('Update not available.');
  });
  autoUpdater.on('update-downloaded', function (
      event, releaseNotes, releaseName, releaseDate, updateUrl, quitAndUpdate) {
    console.log('Update downloaded, quit and update.');
    quitAndUpdate();
  });
  autoUpdater.setFeedUrl('https://net-tsinghua.herokuapp.com/update/osx/' +
                         app.getVersion());

  checkForUpdates = function () {
    autoUpdater.checkForUpdates();
  }
} else if (process.platform == 'win32') {
  // Codes from http://www.mylifeforthecode.com/tag/windows-installer/.
  var updateDotExe = path.resolve(path.dirname(process.execPath),
                                  '..', 'Update.exe');
  var handleSquirrelEvent = function() {
    function executeSquirrelCommand(args, done) {
      var child = cp.spawn(updateDotExe, args, { detached: true });
      child.on('close', function(code) {
        done();
      });
    }

    function install(done) {
      var target = path.basename(process.execPath);
      console.log('Creating shortcut.');
      executeSquirrelCommand(["--createShortcut", target], done);
    }

    function uninstall(done) {
      var target = path.basename(process.execPath);
      console.log('Removing shortcut.');
      executeSquirrelCommand(["--removeShortcut", target], done);
    }

    var squirrelEvent = process.argv[1];
    switch (squirrelEvent) {
      case '--squirrel-install':
        console.log('App installed.');
        install(app.quit);
        return true;
      case '--squirrel-updated':
        console.log('App updated.');
        install(app.quit);
        return true;
      case '--squirrel-obsolete':
        console.log('About to update to a newer version, quit now.');
        app.quit();
        return true;
      case '--squirrel-uninstall':
        console.log('Uninstalling.');
        uninstall(app.quit);
        return true;
    }
    return false;
  };

  if (handleSquirrelEvent()) {
    return;
  }

  checkForUpdates = function () {
    var child = cp.spawn(updateDotExe, [
        "--update",
        "https://net-tsinghua.herokuapp.com/update/win32/" + app.getVersion()
      ], { detached: true });
    child.on('close', function(code) {
      // Update is done, just quit.
      console.log('Update is done. The update should be available next time ' +
                  'you open the app.');
    });
  };
}

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
      save_config();
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

function load_config() {
  console.log('Loading config.');
  config = JSON.parse(fs.readFileSync(__dirname + "/config.json", "utf-8"));
}
load_config();

function save_config() {
  console.log('Saving config.');
  fs.writeFileSync(__dirname + "/config.json", JSON.stringify(config, null, 4), "utf-8");
}

function login() {
  console.log('Logging in.');

  net.login(config.username, config.md5_pass, function (err) {
    if (!err)
      update_all();
  });
}

function logout() {
  console.log('Logging out.');

  net.logout(function (err) {
    if (!err)
      update_all();
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

    var real_time_usage = total_usage;
    sessions.forEach(function (session) { real_time_usage += session.usage; });
    appIcon.setToolTip(STATUS_STR[status] + ' - 本月已用' +
                       utils.usage_str(real_time_usage) + '（实时）');
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

function update_all() {
  update_status();
  update_infos();
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

// Set clocks.
setInterval(refresh_status, config.status_update_interval_msec);
setInterval(refresh_infos, config.info_update_interval_msec);

// FIXME: Looks ugly now.
function account_setting() {
  var dialog = new BrowserWindow({width: 400, height: 220, resizable: true});
  dialog.loadUrl('file://' + __dirname + '/account_setting.html');
  dialog.on('close', function () {
    load_config();
    refresh();
  });
}

app.on('ready', function() {
  appIcon = new Tray(path.join(__dirname, '../resource/icon.png'));

  reset_menu();

  // Tray balloon, currently only supported in Windows.
  if (!config.username) {
    appIcon.displayBalloon({
      title: '未设置帐号',
      content: '点击这里设置帐号\n或者稍后右键点击状态栏图标 > 账号设置'
    });
  }
  appIcon.on('balloon-clicked', function () {
    account_setting();
  });

  refresh();  // First shot.

  checkForUpdates();
});

app.on('window-all-closed', function() {});
