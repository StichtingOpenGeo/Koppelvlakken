def time32(timestamp32):
    hour, minute, second = timestamp32.split(':')
    hour = int(hour)
    if hour > 23:
        hour -= 24
        return '1970-01-02T%.2d:%s:%s'%(hour, minute, second)
    else:
        return '1970-01-01T'+timestamp32
