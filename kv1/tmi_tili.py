class tmi_tili():
    def __init__(self):
        self.data = []
        self.types = [
            {'name': 'UserStopCodeBegin', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'UserStopCodeEnd', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'MinimalDriveTime', 'aard': 'o', 'type': 'N', 'length': 5 },
            {'name': 'Description', 'aard': 'o', 'type': 'A', 'length': 255 },
            ]
        self.references = {'usrstop': ['UserStopCodeBegin'],
                           'usrstop': ['UserStopCodeEnd']}

    def parse(self, version, implicit, data_owner_code, elements):
        user_stop_code_begin, user_stop_code_end, minimal_drive_time, description = elements
        self.data.append([version, implicit, data_owner_code, user_stop_code_begin, user_stop_code_end, minimal_drive_time, description])
