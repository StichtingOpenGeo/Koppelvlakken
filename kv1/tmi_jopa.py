class tmi_jopa():
    def __init__(self):
        self.data = []
        self.types = [
            {'name': 'LinePlanningNumber', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'JourneyPatternCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'JourneyPatternType', 'aard': '+', 'type': 'A', 'length': 10 },
            {'name': 'Direction', 'aard': '+', 'type': 'A', 'length': 1 },
            {'name': 'Description', 'aard': 'o', 'type': 'A', 'length': 255 },
            ]
        self.references = {'line': ['LinePlanningNumber'] }

    def parse(self, version, implicit, data_owner_code, elements):
        line_planning_number, journey_pattern_code, journey_pattern_type, direction, description = elements
        self.data.append([version, implicit, data_owner_code, line_planning_number, journey_pattern_code, journey_pattern_type, direction, description])
