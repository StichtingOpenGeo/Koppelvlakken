class tmi_schedvers():
    def __init__(self):
        self.data = []
        self.types = [
            {'name': 'OrganizationalUnitCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'ScheduleCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'ScheduleTypeCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'ValidFrom', 'aard': '+', 'type': 'D', 'length': 10 },
            {'name': 'ValidThru', 'aard': 'o', 'type': 'D', 'length': 10 },
            {'name': 'Description', 'aard': 'o', 'type': 'A', 'length': 255 },
            ]

    def parse(self, version, implicit, data_owner_code, elements):
        organizational_unit_code, schedule_code, schedule_type_code, valid_from, valid_thru, description = elements
        self.data.append([version, implicit, data_owner_code, organizational_unit_code, schedule_code, schedule_type_code, valid_from, valid_thru, description])
