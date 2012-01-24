class tmi_pegr():
    def __init__(self):
        self.data = []
        self.types = [
            {'name': 'PeriodGroupCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'Description', 'aard': 'o', 'type': 'A', 'length': 255 },
            ]
        self.references = None

    def parse(self, version, implicit, data_owner_code, elements):
        period_group_code, description = elements
        self.data.append([version, implicit, data_owner_code, period_group_code, description])
