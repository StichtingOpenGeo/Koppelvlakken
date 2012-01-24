class tmi_pool():
    def __init__(self):
        self.data = []
        self.types = [
            {'name': 'UserStopCodeBegin', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'UserStopCodeEnd', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'LinkValidFrom', 'aard': '#', 'type': 'D', 'length': 10 },
            {'name': 'PointDataOwnerCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'PointCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'DistanceSinceStartOfLink', 'aard': '+', 'type': 'N', 'length': 5 },
            {'name': 'SegmentSpeed', 'aard': 'o', 'type': 'N', 'length': 4 },
            {'name': 'LocalPointSpeed', 'aard': 'o', 'type': 'N', 'length': 4 },
            {'name': 'Description', 'aard': 'o', 'type': 'A', 'length': 255 },
            {'name': 'TransportType', 'aard': '#', 'type': 'A', 'length': 5 },
            ]
        self.references = {'point': [('PointDataOwnerCode', 'PointCode')],
                           'link': ['UserStopCodeBegin', 'UserStopCodeEnd', 'LinkValidFrom', 'TransportType']}

    def parse(self, version, implicit, data_owner_code, elements):
        user_stop_code_begint, user_stop_code_end, link_valid_from, point_data_owner_code, point_code, distance_since_start_of_link, segment_speed, local_point_speed, description, transport_type = elements
        self.data.append([version, implicit, data_owner_code, user_stop_code_begint, user_stop_code_end, link_valid_from, point_data_owner_code, point_code, distance_since_start_of_link, segment_speed, local_point_speed, description, transport_type])
