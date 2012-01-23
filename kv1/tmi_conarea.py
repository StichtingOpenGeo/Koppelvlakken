class tmi_conarea():
    def __init__(self):
        self.data = []
        self.types = [
            {'name': 'ConcessionAreaCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'Description', 'aard': '+', 'type': 'A', 'length': 255 },
            ]
        self.references = None

    def parse(self, version, implicit, data_owner_code, elements):
        concession_area_code, description = elements
        self.data.append([version, implicit, data_owner_code, concession_area_code, description])
