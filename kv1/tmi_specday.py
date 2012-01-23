class tmi_specday():
    def __init__(self):
        self.data = []
        self.types = [
            {'name': 'SpecificDayCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'Name', 'aard': '+', 'type': 'A', 'length': 50 },
            {'name': 'Description', 'aard': 'o', 'type': 'A', 'length': 255 },
            ]
        self.references = None

    def parse(self, version, implicit, data_owner_code, elements):
        specific_day_code, name, description = elements
        self.data.append([version, implicit, data_owner_code, specific_day_code, name, description])
