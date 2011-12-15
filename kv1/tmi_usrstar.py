class tmi_usrstar():
    def __init__(self):
        self.data = []
        self.types = [
            {'name': 'UserStopAreaCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'Name', 'aard': '+', 'type': 'A', 'length': 50 },
            {'name': 'Town', 'aard': '+', 'type': 'A', 'length': 50 },
            {'name': 'RoadSideEqDataOwnerCode', 'aard': 'o', 'type': 'A', 'length': 10 },
            {'name': 'RoadSideEqUnitNumber', 'aard': 'o', 'type': 'N', 'length': 5 },
            {'name': 'Description', 'aard': 'o', 'type': 'A', 'length': 255 },
            ]

    def parse(self, version, implicit, data_owner_code, elements):
        user_stop_area_code, name, town, road_side_eq_data_owner_code, road_side_eq_unit_number, description = elements
        self.data.append([version, implicit, data_owner_code, user_stop_area_code, name, town, road_side_eq_data_owner_code, road_side_eq_unit_number, description])
