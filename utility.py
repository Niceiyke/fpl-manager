class RiskAssessor:
    @staticmethod
    def assess_injury_risk(player, injury_data):
        return injury_data.get(player['id'], 0)  # 0 = no risk, 1 = minor, 2 = major

    @staticmethod
    def assess_rotation_risk(player, rotation_data):
        return rotation_data.get(player['id'], 0)  # 0 = no risk, 1 = possible, 2 = likely

    @staticmethod
    def advanced_fixture_analysis(player, fixtures, team_data, opponent_data):
        difficulty_score = 0

        for fixture in fixtures:
            if fixture['team_h'] == player['team'] or fixture['team_a'] == player['team']:
                # Determine if player is in the home or away team
                is_home_team = fixture['team_h'] == player['team']
                opponent_team_id = fixture['team_a'] if is_home_team else fixture['team_h']
                fixture_difficulty = fixture['team_h_difficulty'] if is_home_team else fixture['team_a_difficulty']

                # Ensure team_data is a dictionary
                if not isinstance(team_data, dict):
                    raise TypeError("team_data must be a dictionary")

                # Get opponent strength and team strength
                opponent_strength = opponent_data.get(opponent_team_id, {}).get(
                    'strength_defence_home' if is_home_team else 'strength_defence_away', 0)

                # Use appropriate strength based on whether the player’s team is home or away
                team_strength_key = 'strength_attack_home' if is_home_team else 'strength_attack_away'
                team_strength = team_data.get(player['team'], {}).get(team_strength_key, 0)

                # Calculate difficulty score based on fixture difficulty and opponent strength
                difficulty_score += fixture_difficulty - (opponent_strength - team_strength) * 0.5  # Example calculation

        return difficulty_score
