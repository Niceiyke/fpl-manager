from player import PlayerScoreCalculator

class Strategy:
    def __init__(self, risk_tolerance=1, preferred_formation=(1, 4, 4, 2), specific_league=None):
        self.risk_tolerance = risk_tolerance
        self.preferred_formation = preferred_formation
        self.specific_league = specific_league

    def adjust_score_based_on_strategy(self, player_score, player):
        """
        Adjust player score based on user-defined strategy.
        """
        if player['form'] < self.risk_tolerance:
            player_score -= 5  # Penalize players with low form if risk-averse
        if player['position'] not in self.preferred_formation:
            player_score -= 2  # Penalize players not fitting the preferred formation
        
        return player_score

def calculate_strategy_adjusted_score(player, strategy, fixture_difficulty, injury_data, rotation_data, team_data, opponent_data):
    """
    Calculate the player score while considering user-defined strategy.
    """
    base_score =PlayerScoreCalculator.calculate_advanced_player_score(player, fixture_difficulty, injury_data, rotation_data, team_data, opponent_data)
    adjusted_score = strategy.adjust_score_based_on_strategy(base_score, player)
    
    return adjusted_score
