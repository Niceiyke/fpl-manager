import random
from utility import RiskAssessor

class PlayerParser:
    def __init__(self, data, fixtures):
        self.data = data
        self.fixtures = fixtures
        self.players = self.parse_players()

    def parse_players(self):
        if not self.data or not self.fixtures:
            print("Data is missing or in an unexpected format.")
            return {}

        element_types = {1: "goalkeepers", 2: "defenders", 3: "midfielders", 4: "forwards"}
        players = {position: [] for position in element_types.values()}

        team_fixtures = {team['id']: [] for team in self.data['teams']}
        for fixture in self.fixtures:
            if not fixture['finished']:
                home_difficulty = fixture['team_h_difficulty']
                away_difficulty = fixture['team_a_difficulty']
                team_fixtures[fixture['team_h']].append(home_difficulty)
                team_fixtures[fixture['team_a']].append(away_difficulty)

        avg_fixture_difficulty = {
            team_id: sum(difficulties) / len(difficulties) if len(difficulties) > 0 else 0
            for team_id, difficulties in team_fixtures.items()
        }

        for player in self.data['elements']:
            position = element_types[player['element_type']]
            team_id = player['team']
            form = float(player['form'])
            fixture_difficulty = avg_fixture_difficulty[team_id]

            if player['status'] in ['i', 'd']:
                continue

            players[position].append({
                "id": player['id'],
                "name": player['web_name'],
                "position": player['element_type'],
                "status": player['status'],
                "ict_index": player['ict_index'],
                "price": player['now_cost'] / 10,
                "points": player['total_points'],
                "expected_goals": player['expected_goals'],
                "expected_assists": player['expected_assists'],
                "expected_goal_involvements": player['expected_goal_involvements'],
                'saves_per_90': player['saves_per_90'],
                "goals_conceded_per_90": player['goals_conceded_per_90'],
                "bonus": player['bonus'],
                "expected_point": player['ep_next'],
                "form": form,
                "fixture_difficulty": fixture_difficulty,
                "team": player['team'],
                "starts": player['starts'],
            })

        return players
    
    def calculate_upcoming_fixture_difficulty(self, num_weeks=5):
        team_fixtures = {team['id']: [] for team in self.data['teams']}
        
        for fixture in self.fixtures:
            if not fixture['finished']:
                home_team = fixture['team_h']
                away_team = fixture['team_a']
                
                # Only consider fixtures within the upcoming num_weeks
                if fixture['event'] <= num_weeks:
                    team_fixtures[home_team].append(fixture['team_h_difficulty'])
                    team_fixtures[away_team].append(fixture['team_a_difficulty'])

        avg_fixture_difficulty = {
            team_id: sum(difficulties) / len(difficulties) if len(difficulties) > 0 else 0
            for team_id, difficulties in team_fixtures.items()
        }

        return avg_fixture_difficulty


class PlayerScoreCalculator:
    def __init__(self, injury_data, rotation_data, team_data, opponent_data):
        self.injury_data = injury_data
        self.rotation_data = rotation_data
        self.team_data = team_data
        self.opponent_data = opponent_data

    def calculate_player_score(self, player, fixture_difficulty):
        base_score = (player["form"] * 2) - fixture_difficulty + (player["points"] / 10)
        injury_risk = RiskAssessor.assess_injury_risk(player, self.injury_data)
        rotation_risk = RiskAssessor.assess_rotation_risk(player, self.rotation_data)
        fixture_difficulty_score = RiskAssessor.advanced_fixture_analysis(
            player, [fixture for fixture in self.opponent_data[player['team']]],
            self.team_data, self.opponent_data)

        # Adjust score based on risks and advanced fixture analysis
        score = base_score - (injury_risk * 2) - (rotation_risk * 2) - (fixture_difficulty_score / 10)
        return score
    def fetch_advanced_metrics(player_id):
        """
        Fetch advanced metrics like xG, xA, and shots on target for a player.
        """
        # Simulated API response
        response = {
            'xG': random.uniform(0, 1),
            'xA': random.uniform(0, 1),
            'shots_on_target': random.randint(0, 5)
        }
        
        return response

    def calculate_advanced_player_score(player, fixture_difficulty, injury_data, rotation_data, team_data, opponent_data):
            """
            Calculate player score using advanced metrics.
            """
            base_score = (player["form"] * 2) - fixture_difficulty + (player["points"] / 10)
            injury_risk = RiskAssessor.assess_injury_risk(player, injury_data)
            rotation_risk = RiskAssessor.assess_rotation_risk(player, rotation_data)
            fixture_difficulty_score = RiskAssessor.advanced_fixture_analysis(player, [fixture for fixture in opponent_data[player['team']]], team_data, opponent_data)
            
            # Fetch advanced metrics
            metrics = PlayerScoreCalculator.fetch_advanced_metrics(player['id'])
            xG, xA, shots_on_target = metrics['xG'], metrics['xA'], metrics['shots_on_target']
            
            # Adjust score based on advanced metrics
            score = base_score + (xG + xA) * 2 + shots_on_target * 0.5 - (injury_risk * 2) - (rotation_risk * 2) - (fixture_difficulty_score / 10)
            
            return score
    
  