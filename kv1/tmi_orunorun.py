class tmi_orunorun():
    def __init__(self):
        self.data = []
        self.types = [
            {'name': 'OrganizationalUnitcodeParent', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'OrganizationalUnitcodeChild', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'Validfrom', 'aard': '#', 'type': 'D', 'length': 10 } ]
        self.references = {'orun': ['OrganizationalUnitcodeParent'], 
                           'orun': ['OrganizationalUnitcodeChild']}

    def parse(self, version, implicit, data_owner_code, elements):
        organizational_unitcode_parent, organizational_unitcode_child, validfrom = elements
        self.data.append([version, implicit, data_owner_code, organizational_unitcode_parent, organizational_unitcode_child, validfrom])
