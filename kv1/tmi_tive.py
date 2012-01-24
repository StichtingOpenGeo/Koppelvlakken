class tmi_tive():
    def __init__(self):
        self.data = []
        self.types = [
            {'name': 'OrganizationalUnitCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'TimetableVersionCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'PeriodGroupCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'SpecificDayCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'ValidFrom', 'aard': '+', 'type': 'D', 'length': 10 },
            {'name': 'TimetableVersionType', 'aard': '+', 'type': 'A', 'length': 10 },
            {'name': 'ValidThru', 'aard': 'o', 'type': 'D', 'length': 10 },
            {'name': 'Description', 'aard': 'o', 'type': 'A', 'length': 255 } ]
        self.references = {'orun': ['OrganizationalUnitCode'],
                           'specday': ['SpecificDayCode'],
                           'pegr': ['PeriodGroupCode']}

    def parse(self, version, implicit, data_owner_code, elements):
        organizational_unit_code, timetable_version_code, period_group_rode, specific_day_code, valid_from, timetable_version_type, valid_thru, description = elements
        self.data.append([version, implicit, data_owner_code, organizational_unit_code, timetable_version_code, period_group_rode, specific_day_code, valid_from, timetable_version_type, valid_thru, description])
