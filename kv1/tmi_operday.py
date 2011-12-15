class tmi_operday():
    def __init__(self):
        self.data = []
        self.types = [
            {'name': 'OrganizationalUnitCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'ScheduleCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'ScheduleTypeCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'ValidDate', 'aard': '#', 'type': 'D', 'length': 10 },
            {'name': 'Description', 'aard': 'o', 'type': 'A', 'length': 255 },
            ]

    def parse(self, version, implicit, data_owner_code, elements):
        organizational_unit_code, schedule_code, schedule_type_code, valid_date, description = elements 
        self.data.append([version, implicit, data_owner_code, organizational_unit_code, schedule_code, schedule_type_code, valid_date, description])
