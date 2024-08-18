class FPLConfig:
    def __init__(self, availability_weight=1.0, differential_thresholds=None, cost_efficiency_weight=1.0, 
                 set_piece_weight=1.0, fdr_weight=1.0, recent_form_weight=1.0, rotation_risk_weight=1.0, 
                 team_strength_weight=1.0, xg_xa_weight=1.0,defender_defensive_weight=1.0,
                 defender_attacking_weight=2.0,middlefilders_defensive_weight=1.0,middlefilders_attacking_weight=5.0,
                 forward_defensive_weight=1.0,forward_attacking_weight=10.0,goalkeapers_defensive_weight=1.0,):
        self.availability_weight = availability_weight
        self.differential_thresholds = differential_thresholds if differential_thresholds else {5: 1.2, 20: 1, 100: 0.9}
        self.cost_efficiency_weight = cost_efficiency_weight
        self.set_piece_weight = set_piece_weight
        self.fdr_weight = fdr_weight
        self.recent_form_weight = recent_form_weight
        self.rotation_risk_weight = rotation_risk_weight
        self.team_strength_weight = team_strength_weight
        self.xg_xa_weight = xg_xa_weight
        self.defender_defensive_weight = defender_defensive_weight
        self.defender_attacking_weight = defender_attacking_weight
        self.middlefilders_defensive_weight = middlefilders_defensive_weight
        self.middlefilders_attacking_weight = middlefilders_attacking_weight
        self.forward_defensive_weight = forward_defensive_weight
        self.forward_attacking_weight = forward_attacking_weight
        self.goalkeapers_defensive_weight = goalkeapers_defensive_weight
