class tmi_excopday():
    def __init__(self):
        self.data = []
        self.types = [
            {'name': 'OrganizationalUnitCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'ValidDate', 'aard': '#', 'type': 'TS', 'length': 23 },
            {'name': 'DayTypeAsOn', 'aard': '+', 'type': 'N', 'length': 7 },
            {'name': 'SpecificDayCode', 'aard': '+', 'type': 'A', 'length': 10 },
            {'name': 'PeriodGroupCode', 'aard': 'o', 'type': 'A', 'length': 10 },
            {'name': 'Description', 'aard': 'o', 'type': 'A', 'length': 255 },
            ]

    def parse(self, version, implicit, data_owner_code, elements):
        organizational_unit_code, valid_date, day_type_as_on, specific_day_code, period_group_code, description = elements
        self.data.append([version, implicit, data_owner_code, organizational_unit_code, valid_date, day_type_as_on, specific_day_code, period_group_code, description])
