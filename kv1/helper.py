def time32(timestamp32):
    hour, minute, second = timestamp32.split(':')
    hour = int(hour)
    if hour > 23:
        hour -= 24
        return '1970-01-02T%.2d:%s:%s'%(hour, minute, second)
    else:
        return '1970-01-01T'+timestamp32

def wheelchair(wheel_chair_accessible):
    if (wheel_chair_accessible == 'ACCESSIBLE'):
        wheel_chair_accessible = 'true'
    elif (wheel_chair_accessible == 'NOTACCESSIBLE'):
        wheel_chair_accessible = 'false'
    else:
        wheel_chair_accessible = ''

    return wheel_chair_accessible

def boolsql(boolean):
    if boolean:
        return 'true'
    else:
        return 'false'
