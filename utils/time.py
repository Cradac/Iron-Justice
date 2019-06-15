from datetime import date, time, datetime, timedelta

timezone = {
    'IDLW': -12,
    'NT': -11,
    'CAT': -10,
    'HAST': -10,
    'HST': -10,
    'YST': -9,
    'AKST': -9,
    'HDT': -9,
    'PST': -8,
    'HADT': -8,
    'YDT': -8,
    'AKDT': -8,
    'MST': -7,
    'PDT': -7,
    'CST': -6,
    'MDT': -6,
    'EST': -5,
    'CDT': -5,
    'AST': -4,
    'EDT': -4,
    'ART': -3,
    'ADT': -3,
    'AT': -2,
    'GMT': 0,
    'UTC': 0,
    'UT': 0,
    'WET': 0,
    'CET': 1,
    'WAT': 1,
    'BST': 1,
    'IST': 1,
    'WEDT': 1,
    'WEST': 1,
    'EET': 2,
    'USZ1': 2,
    'CEDT': 2,
    'CEST': 2,
    'MEST': 2,
    'MESZ': 2,
    'MSK': 3,
    'EAT': 3,
    'EEDT': 3,
    'EEST': 3,
    'SMT': 4,
    'AMT': 4,
    'AZT': 4,
    'GET': 4,
    'MUT': 4,
    'PKT': 5,
    'YEKT': 5,
    'MVT': 5,
    'OMSK': 6,
    'CXT': 7,
    'KRAT': 7,
    'IRKT': 8,
    'AWST': 8,
    'WADT': 8,
    'JST': 9,
    'YAKT': 9,
    'EAST': 10,
    'VLAT': 10,
    'SAKT': 11,
    'EADT': 11,
    'IDLE': 12,
    'NZST': 12,
    'NZT': 12,
    'MAGT': 12,
    'NZDT': 13,
}

def parse_time(ctx, time_str:str):
    time = None
    try:
        time = time.strptime(time_str, '%r')
        return time
    except:
        try:
            time = time.strptime(time_str, '%R')
            return time
        except:
            pass
    if time_str[-2:].upper() in ('AM', 'PM', 'A', 'P'):
        try:
            time = time.strptime(time_str, '%I:%M%P')
        except:
            try:
                time = time.strptime(time_str, '%I:%M %P')
            except:
                try:
                    time = time.strptime(time_str, '%I.%M%P')
                except:
                    try:
                        time = time.strptime(time_str, '%I.%M %P')
                    except:
                        ctx.send('Couldn\'t parse time string. Use `.` or `:` to seperate hour and minute. You can either use 12 or 24 hour format.')
                        return None
    else:
        try:
            time = time.strptime(time_str, '%H:%M')
        except:
            try:
                time = time.strptime(time_str, '%H:%M')
            except:
                ctx.send('Couldn\'t parse time string. Use `.` or `:` to seperate hour and minute. You can either use 12 or 24 hour format.')
                return None
    return time

def calc_time(ctx, time_str: str, timezone_str: str):
    time = parse_time(ctx, time_str)
    if not time:
        return
    tz = timezone.get(timezone_str)
    if not tz:
        ctx.send('Timezone key not found. To see all available keys go here: <https://greenwichmeantime.com/time-zone/definition/>')
        return
    end_time = time + timedelta(hours=tz)
    return end_time
