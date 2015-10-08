exports.usage_str = function usage_srt(usage) {
  if (usage == null)
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
