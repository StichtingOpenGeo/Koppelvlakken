class tmi_timdemgrp():
    def __init__(self):
        self.data = []
        self.types = [
            {'name': 'LinePlanningNumber', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'JourneyPatternCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'TimeDemandGroupCode', 'aard': '#', 'type': 'A', 'length': 10 },
            ]
        self.references = {'jopa': ['LinePlanningNumber', 'JourneyPatternCode']}

    def parse(self, version, implicit, data_owner_code, elements):
        line_planning_number, journey_pattern_code, time_demand_group_code = elements
        self.data.append([version, implicit, data_owner_code, line_planning_number, journey_pattern_code, time_demand_group_code])
