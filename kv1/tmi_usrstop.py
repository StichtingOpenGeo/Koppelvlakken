class tmi_usrstop():
    def __init__(self):
        self.data = []
        self.types = [
            {'name': 'UserStopCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'TimingPointCode', 'aard': 'o', 'type': 'A', 'length': 10 },
            {'name': 'GetIn', 'aard': '+', 'type': 'B', 'length': 5 },
            {'name': 'GetOut', 'aard': '+', 'type': 'B', 'length': 5 },
            {'name': 'Name', 'aard': '+', 'type': 'A', 'length': 50 },
            {'name': 'Town', 'aard': '+', 'type': 'A', 'length': 50 },
            {'name': 'UserStopAreaCode', 'aard': 'o', 'type': 'A', 'length': 10 },
            {'name': 'StopSideCode', 'aard': 'o', 'type': 'A', 'length': 10 },
            {'name': 'RoadSideEqDataOwnerCode', 'aard': 'o', 'type': 'A', 'length': 10 },
            {'name': 'RoadSideEqUnitNumber', 'aard': 'o', 'type': 'N', 'length': 5 },
            {'name': 'MinimalStopTime', 'aard': '+', 'type': 'N', 'length': 5 },
            {'name': 'StopSideLength', 'aard': 'o', 'type': 'N', 'length': 3 },
            {'name': 'Description', 'aard': 'o', 'type': 'A', 'length': 255 },
            {'name': 'UserStopType', 'aard': '+', 'type': 'A', 'length': 10 },
            ]
        # This is a weak references
        # self.references = {'usrstar': ['UserStopAreaCode']}
        self.references = None

    def parse(self, version, implicit, data_owner_code, elements):
        user_stop_code, timing_point_code, get_in, get_out, _, name, town, user_stop_area_code, stop_side_code, road_side_eq_data_owner_code, road_side_eq_unit_number, minimal_stop_time, stop_side_length, description, user_stop_type = elements
        if stop_side_code == '-':
            stop_side_code = ''
        self.data.append([version, implicit, data_owner_code, user_stop_code, timing_point_code, get_in, get_out, name, town, user_stop_area_code, stop_side_code, road_side_eq_data_owner_code, road_side_eq_unit_number, minimal_stop_time, stop_side_length, description, user_stop_type])
