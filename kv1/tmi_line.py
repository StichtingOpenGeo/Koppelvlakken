class tmi_line():
    def __init__(self):
        self.data = []
        self.types = [
            {'name': 'LinePlanningNumber', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'LinePublicNumber', 'aard': '+', 'type': 'A', 'length': 4 },
            {'name': 'LineName', 'aard': '+', 'type': 'A', 'length': 50 },
            {'name': 'LineVeTagNumber', 'aard': '+', 'type': 'N', 'length': 3 },
            {'name': 'Description', 'aard': 'o', 'type': 'A', 'length': 255 },
            {'name': 'TransportType', 'aard': '+', 'type': 'A', 'length': 5 },
            ]

    def parse(self, version, implicit, data_owner_code, elements):
        line_planning_number, line_public_number, line_name, line_ve_tag_number, description, transport_type = elements
        if line_ve_tag_number == '':
            print elements
        self.data.append([version, implicit, data_owner_code, line_planning_number, line_public_number, line_name, line_ve_tag_number, description, transport_type])
