from helper import time32, wheelchair

class tmi_pujopass():
    def __init__(self):
        self.data = []
        self.types = [
            {'name': 'OrganizationalUnitCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'ScheduleCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'ScheduleTypeCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'LinePlanningNumber', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'JourneyNumber', 'aard': '#', 'type': 'N', 'length': 6 },
            {'name': 'StopOrder', 'aard': '#', 'type': 'N', 'length': 4 },
            {'name': 'JourneyPatternCode', 'aard': '+', 'type': 'A', 'length': 10 },
            {'name': 'UserStopCode', 'aard': '+', 'type': 'A', 'length': 10 },
            {'name': 'TargetArrivalTime', 'aard': 'o', 'type': 'T', 'length': 8 },
            {'name': 'TargetDepartureTime', 'aard': 'o', 'type': 'T', 'length': 8 },
            {'name': 'WheelChairAccessible', 'aard': '+', 'type': 'B', 'length': 5 },
            {'name': 'DataOwnerIsOperator', 'aard': '+', 'type': 'B', 'length': 5 },
            ]
        self.references = {'schedvers': ['OrganizationalUnitCode', 'ScheduleCode', 'ScheduleTypeCode'],
                           'jopa': ['JourneyPatternCode'],
                           'usrstop': ['UserStopCode']}

    def parse(self, version, implicit, data_owner_code, elements):
        organizational_unit_code, schedule_code, schedule_type_code, line_planning_number, journey_nuwber, stop_order, journey_pattern_code, user_stop_code, target_arrival_time, target_departure_time, wheel_chair_accessible, data_owner_is_operator = elements

        target_arrival_time = time32(target_arrival_time)
        target_departure_time = time32(target_departure_time)
        wheel_chair_accessible = wheelchair(wheel_chair_accessible)

        self.data.append([version, implicit, data_owner_code, organizational_unit_code, schedule_code, schedule_type_code, line_planning_number, journey_nuwber, stop_order, journey_pattern_code, user_stop_code, target_arrival_time, target_departure_time, wheel_chair_accessible, data_owner_is_operator])
