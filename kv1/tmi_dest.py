class tmi_dest():
    def __init__(self):
        self.data = []
        self.types = [
            {'name': 'DestCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'DestNameFull', 'aard': '+', 'type': 'A', 'length': 50 },
            {'name': 'DestNameMain', 'aard': '+', 'type': 'A', 'length': 24 },
            {'name': 'DestNameDetail', 'aard': 'o', 'type': 'A', 'length': 24 },
            {'name': 'RelevantDestNameDetail', 'aard': '+', 'type': 'B', 'length': 5 },
            ]
        self.reference = None

    def parse(self, version, implicit, data_owner_code, elements):
        dest_code, dest_name_full, dest_name_mail, dest_name_detail, relevant_dest_name_detail = elements
        self.data.append([version, implicit, data_owner_code, dest_code, dest_name_full, dest_name_mail, dest_name_detail, relevant_dest_name_detail])
