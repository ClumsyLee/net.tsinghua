var app = require('app');
var Menu = require('menu');
var Tray = require('tray');

var fs = require('fs');
var config = JSON.parse(fs.readFileSync("./config.json", "utf-8"));

var net = require('./net');
var utils = require('./utils')

var status = 'UNKNOWN';
var last_session = null;
var last_check = null
var sessions = [];
var balance = null;
var usage = null;

var STATUS_STR = {
  UNKNOWN: '未知状态',
  OFFLINE: '离线',
  ONLINE: '在线',
  OTHERS_ACCOUNT_ONLINE: '他人账号在线',
  ERROR: '网络错误',
  NO_CONNECTION: '无连接'
}

function get_menu_template() {
  var template = [];

  // Status.
  var status_str = STATUS_STR[status];
  // Show session usage if possible.
  if ((status == 'ONLINE' || status == 'OTHERS_ACCOUNT_ONLINE') && last_session)
    status_str = status_str + '-' + utils.usage_str(last_session.usage);
  template.push({label: status_str, enabled: false});

  // Account info.
  template.push({type: 'separator'});
  if (!config.username) {
    template.push({label: '未设置帐号', enabled: false});
  } else {
    template.push({label: config.username, enabled: false});
    template.push({label: '本月流量：' + utils.usage_str(usage), enabled: false});
    template.push({label: '当前余额：' + utils.balance_str(balance),
                   enabled: false});
  }

  // Sessions.
  template.push({type: 'separator'});
  if (!sessions) {
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
    {label: '上线', click: function () {
      net.login(config.username, config.md5_pass);
    }},
    {label: '下线', click: function() {net.logout();}},
    {label: '现在刷新'},

    // Config.
    {type: 'separator'},
    {label: '自动管理', type: 'checkbox', checked: config.auto_manage},
    {label: '账号设置...'},

    // About.
    {type: 'separator'},
    {label: '关于 net.tsinghua', role: 'about'},

    // Quit.
    {type: 'separator'},
    {label: '退出', click: function() {app.quit();}}
  ]);
}

var appIcon = null;
app.on('ready', function(){
  appIcon = new Tray('icon.png');

  // template[0].label = 'hehe';
  var contextMenu = Menu.buildFromTemplate(get_menu_template());
  appIcon.setContextMenu(contextMenu);
  appIcon.setToolTip('This is my application.');
});
