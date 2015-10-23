var encoding = require('encoding');

exports.time_passed_str = function time_passed_str(t) {
  if (t == null)
    return '从未';

  var delta = Date.now() - t.getTime();

  var minute = 60 * 1000;
  var hour = 60 * minute;
  var day = 24 * hour;

  if (delta < minute)
    return '刚刚';
  else if (delta < hour)
    return (delta / minute).toFixed(0) + '分钟前';
  else if (delta < day)
    return (delta / hour).toFixed(0) + '小时前';
  else
    return (delta / day).toFixed(0) + '天前';
}

exports.usage_str = function usage_str(usage) {
  if (usage == null || isNaN(usage))
    return '未知';
  else if (usage < 1e3)
    return usage.toString() + 'B';
  else if (usage < 1e6)
    return (usage / 1e3).toFixed(2) + 'K'
  else if (usage < 1e9)
    return (usage / 1e6).toFixed(2) + 'M'
  else
    return (usage / 1e9).toFixed(2) + 'G'
}

exports.parse_usage_str = function parse_usage_str(s) {
  var num = Number(s.substr(0, s.length - 1));
  var unit = s[s.length - 1].toUpperCase();

  var ratio;
  switch (unit) {
    case 'B': ratio = 1;   break;
    case 'K': ratio = 1e3; break;
    case 'M': ratio = 1e6; break;
    case 'G': ratio = 1e9; break;
  }

  return Math.round(num * ratio);
}

exports.balance_str = function balance_str(balance) {
  if (balance == null)
    return '未知';
  else
    return balance.toFixed(2) + '元';
}

exports.gb2312_to_utf8 = function gb2312_to_utf8(s) {
  return encoding.convert(s, 'UTF-8', 'GB2312').toString();
}
