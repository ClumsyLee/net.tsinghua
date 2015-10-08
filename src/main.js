var app = require('app');
var Menu = require('menu');
var Tray = require('tray');

var fs = require('fs');
var config = JSON.parse(fs.readFileSync("./config.json", "utf-8"));

var net = require('./net');

var submenu_template = [
  {label: '59.66.1.1', enabled: false},
  {label: '5分钟前上线', enabled: false},
  {label: '≥ 14.32M', enabled: false},
  {label: '下线'}
];

var template = [
  {label: '未知', enabled: false},
  {type: 'separator'},
  {label: 'lisihan13', enabled: false},
  {label: '本月流量', enabled: false},
  {label: '当前余额', enabled: false},
  {type: 'separator'},
  {label: '当前在线', enabled: false},
  {label: 'IOS', submenu: submenu_template},
  {label: '上次更新', enabled: false},
  {type: 'separator'},
  {label: '上线', click: function () {
    net.login(config.username, config.md5_pass);
  }},
  {label: '下线', click: function() {net.logout();}},
  {label: '现在刷新'},
  {type: 'separator'},
  {label: '自动管理', type: 'checkbox', checked: config.auto_manage},
  {label: '账号设置...'},
  {type: 'separator'},
  {label: '关于'},
  {type: 'separator'},
  {label: '退出', click: function() {app.quit();}}
];

var appIcon = null;
app.on('ready', function(){
  appIcon = new Tray('icon.png');

  // var submenu = Menu.buildFromTemplate(submenu_template);
  var contextMenu = Menu.buildFromTemplate(template);
  appIcon.setToolTip('This is my application.');
  appIcon.setContextMenu(contextMenu);
});
