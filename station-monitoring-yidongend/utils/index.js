// utils.js
export let typeContrast = {
    heartRate: '心率'
}
//判断是否为空
export function isEmpty(v) {
    switch (typeof v) {
    case 'undefined':
        return true;
    case 'string':
        if (v.replace(/(^[ \t\n\r]*)|([ \t\n\r]*$)/g, '').length == 0) return true;
        break;
    case 'boolean':
        if (!v) return true;
        break;
    case 'number':
        if (0 === v || isNaN(v)) return true;
        break;
    case 'object':
        if (null === v || v.length === 0) return true;
        for (var i in v) {
            return false;
        }
        return true;
    }
    return false;
}
//格式化日期
export function formatDate(date, format) {
    var d = new Date(date),
        year = d.getFullYear(),
        month = '' + (d.getMonth() + 1), // 月份是从0开始的
        day = '' + d.getDate(),
        hours = '' + d.getHours(),
        minutes = '' + d.getMinutes(),
        seconds = '' + d.getSeconds();

    // 补齐月份、日期、小时、分钟和秒数的前导0
    if (month.length < 2) month = '0' + month;
    if (day.length < 2) day = '0' + day;
    if (hours.length < 2) hours = '0' + hours;
    if (minutes.length < 2) minutes = '0' + minutes;
    if (seconds.length < 2) seconds = '0' + seconds;

    if (format) {
        // 根据格式字符串替换对应的日期时间组成部分
        return format.replace('YYYY', year)
                     .replace('MM', month)
                     .replace('DD', day)
                     .replace('HH', hours)
                     .replace('mm', minutes) // 注意这里需要小写的mm表示分钟
                     .replace('SS', seconds);
    } else {
        return [year, month, day].join('-') + ' ' + [hours, minutes, seconds].join(':');
    }
}

// 添加秒数
export function addSeconds(date, seconds) {
	  // 将日期转换为时间戳（以毫秒为单位）
	  var timestamp = date.getTime();
	  // 添加指定的秒数（转换为毫秒）
	  var newTimestamp = timestamp + (seconds * 1000);
	  // 将新的时间戳转换回 Date 对象
	  var newDate = new Date(newTimestamp);
	  // 返回格式化后的日期字符串
	  return formatDate(newDate, 'YYYY-MM-DD HH:mm:SS');
	}