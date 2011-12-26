class tmi_jopatili():
    def __init__(self):
        self.data = []
        self.types = [
            {'name': 'LinePlanningNumber', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'JourneyPatternCode', 'aard': '#', 'type': 'A', 'length': 10 },
            {'name': 'TimingLinkOrder', 'aard': '#', 'type': 'N', 'length': 3 },
            {'name': 'UserStopCodeBegin', 'aard': '+', 'type': 'A', 'length': 10 },
            {'name': 'UserStopCodeEnd', 'aard': '+', 'type': 'A', 'length': 10 },
            {'name': 'ConFinRelCode', 'aard': '+', 'type': 'A', 'length': 10 },
            {'name': 'DestCode', 'aard': '+', 'type': 'A', 'length': 10 },
            {'name': 'IsTimingStop', 'aard': '+', 'type': 'B', 'length': 5 },
            {'name': 'DisplayPublicLine', 'aard': 'o', 'type': 'A', 'length': 4 },
            {'name': 'ProductFormulaType', 'aard': 'o', 'type': 'A', 'length': 4 },
            ]

    def parse(self, version, implicit, data_owner_code, elements):
        line_planning_number, journey_pattern_code, timing_link_order, user_stop_code_begin, user_stop_code_end, con_fin_rel_code, dest_code, _, is_timing_stop, display_public_line, product_formula_type = elements
        self.data.append([version, implicit, data_owner_code, line_planning_number, journey_pattern_code, timing_link_order, user_stop_code_begin, user_stop_code_end, con_fin_rel_code, dest_code, is_timing_stop, display_public_line, product_formula_type])
