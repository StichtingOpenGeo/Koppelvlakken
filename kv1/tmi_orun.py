class tmi_orun():
    def __init__(self):
        self.data = []
        self.types = [
            {'name': 'OrganizationalUnitCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'Name', 'aard': '+', 'type': 'A', 'length': 50 },
            {'name': 'OrganizationalUnitType', 'aard': '+', 'type': 'A', 'length': 10 },
            {'name': 'Description', 'aard': 'o', 'type': 'A', 'length': 255 } ]
        self.references = None

    def parse(self, version, implicit, data_owner_code, elements):
        organizational_unit_code, name, organization_unit_type, description = elements
        self.data.append([version, implicit, data_owner_code, organizational_unit_code, name, organization_unit_type, description])
