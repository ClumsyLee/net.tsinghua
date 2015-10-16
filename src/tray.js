var path = require('path');

var app = require('app');
var EventEmitter = require('events');
var Menu = require('menu');
var shell = require('shell');
var Tray = require('tray');

var utils = require('./utils');

module.exports = new EventEmitter();

var STATUS_STR = {
  UNKNOWN: '未知状态',
  OFFLINE: '离线',
  ONLINE: '在线',
  OTHERS_ACCOUNT_ONLINE: '他人账号在线',
  ERROR: '网络错误',
  NO_CONNECTION: '无连接'
};
var tray;

template = [
  {enabled: false, id: 'status'},

  // Account info.
  {type: 'separator', id: 'account_info'},
  {enabled: false, id: 'username'},

  // Sessions.
  {type: 'separator', id: 'sessions'},

  // Actions.
  {type: 'separator'},
  {label: '上线', click: function () { module.exports.emit('login'); }},
  {label: '下线', click: function () { module.exports.emit('logout'); }},
  {label: '现在刷新', click: function () { module.exports.emit('refresh'); }},

  // Config.
  {type: 'separator'},
  {label: '自动管理', type: 'checkbox', id: 'auto_manage',
   click: function (item) { module.exports.emit('auto_manage_changed', item.checked); }},
  {label: '账号设置...', click: function () { module.exports.emit('account_setting'); }},

  // About.
  {type: 'separator'},
  {label: '关于 ' + app.getName(), click: function () {
    shell.openExternal('https://github.com/ThomasLee969/net.tsinghua');
  }},

  // Quit.
  {type: 'separator'},
  {label: '退出', click: function() { app.quit(); }}
];

function build_account_info(infos) {
  return [
    {
      label: '本月流量：' + utils.usage_str(infos.total_usage),
      enabled: false,
      position: 'endof=account_info'
    }, {
      label: '当前余额：' + utils.balance_str(infos.balance),
      enabled: false,
      position: 'endof=account_info'
    }
  ];
}

function build_sessions(infos) {
  sessions = [];

  infos.sessions.forEach(function (session) {
    var label = session.device_name;
    if (session.ip == infos.last_session.ip)  // Current session.
      label += '（本机）';

    sessions.push({
      label: label,
      submenu: [
        {label: session.ip, enabled: false},
        {label: utils.time_passed_str(session.start_time) + '上线', enabled: false},
        {label: '≥ ' + utils.usage_str(session.usage), enabled: false},
        {label: '下线', click: function () { module.exports.emit('logout_session',
                                                                session.id); }}
      ],
      position: 'endof=sessions'
    });
  });

  return sessions;
}

// Build a map.
template_map = {};
template.forEach(function (element) {
  if (element.id)
    template_map[element.id] = element;
});

function real_time_usage_str(infos) {
  var real_time_usage = infos.total_usage;
  infos.sessions.forEach(function (session) { real_time_usage += session.usage; });
  return '实时流量 ' + utils.usage_str(real_time_usage);
}

module.exports.reset_menu = function reset_menu(infos) {
  console.log('Reseting menu.');
  var extras = [];

  // Status.
  var status_str = STATUS_STR[infos.status];
  // Show session usage if possible.
  if ((infos.status == 'ONLINE' || infos.status == 'OTHERS_ACCOUNT_ONLINE') &&
      infos.last_session)
    status_str += ' - ' + utils.usage_str(infos.last_session.usage);
  template_map.status.label = status_str;

  // Account info.
  if (infos.username) {
    template_map.username.label = infos.username;
    extras = extras.concat(build_account_info(infos));
  } else {
    template_map.username.label = '未设置帐号';
  }

  // Sessions.
  if (infos.sessions.length == 0) {
    extras.push({label: '无设备在线', enabled: false, position: 'endof=sessions'});
  } else {
    extras.push({label: '当前在线', enabled: false, position: 'endof=sessions'});
    extras = extras.concat(build_sessions(infos));
  }

  // FIXME: Currently it seems there's not menu.aboutToShow.
  // So time will be valid only when status_update_interval_msec < 60s.
  extras.push({
    label: '上次更新：' + utils.time_passed_str(infos.last_check),
    enabled: false,
    position: 'endof=sessions'
  });

  tray.setContextMenu(Menu.buildFromTemplate(template.concat(extras)));
  tray.setToolTip(STATUS_STR[infos.status] + ' - ' + real_time_usage_str(infos));
}

app.on('ready', function () {
  tray = new Tray(path.join(__dirname, '../resource/tray_icon_Template.png'));
});
