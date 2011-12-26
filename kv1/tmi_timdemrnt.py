class tmi_timdemrnt():
    def __init__(self):
        self.data = []
        self.types = [
            {'name': 'LinePlanningNumber', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'JourneyPatternCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'TimeDemandGroupCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'TimingLinkOrder', 'aard': '#', 'type': 'N', 'length': 3 },
            {'name': 'UserStopCodeBegin', 'aard': '+', 'type': 'A', 'length': 10 },
            {'name': 'UserStopCodeEnd', 'aard': '+', 'type': 'A', 'length': 10 },
            {'name': 'TotalDriveTime', 'aard': '+', 'type': 'N', 'length': 5 },
            {'name': 'DriveTime', 'aard': '+', 'type': 'N', 'length': 5 },
            {'name': 'ExpectedDelay', 'aard': 'o', 'type': 'N', 'length': 5 },
            {'name': 'LayOverTime', 'aard': 'o', 'type': 'N', 'length': 5 },
            {'name': 'StopWaitTime', 'aard': '+', 'type': 'N', 'length': 5 },
            {'name': 'MinimumStopTime', 'aard': 'o', 'type': 'N', 'length': 5 },
            ]

    def parse(self, version, implicit, data_owner_code, elements):
        line_planning_number, journey_pattern_code, time_demand_group_order, timing_link_order, user_stop_code_begin, user_stop_code_end, total_drive_time, drive_time, expected_delay, lay_over_time, stop_wait_time, minimum_stop_time = elements
        self.data.append([version, implicit, data_owner_code, line_planning_number, journey_pattern_code, time_demand_group_order, timing_link_order, user_stop_code_begin, user_stop_code_end, total_drive_time, drive_time, expected_delay, lay_over_time, stop_wait_time, minimum_stop_time])
