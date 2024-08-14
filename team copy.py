import heapq

import requests
from data import FIXTURES_API_URL
from player import PlayerScoreCalculator
from pulp import LpMaximize, LpProblem, LpVariable, lpSum,LpStatus

from strategy import Strategy
from player import PlayerScoreCalculator

class TeamData:
    def __init__(self, teams):
        self.teams = teams
    def calculate_opponent_strengths(self):
        opponent_data = {}
        for team in self.teams:
            team_id = team['id']
            defensive_strength = team['strength_defence_home'] + team['strength_defence_away']
            offensive_strength = team['strength_attack_home'] + team['strength_attack_away']

            opponent_data[team_id] = {
                "defensive_strength": defensive_strength / 2.0,  # Averaging home and away strength
                "offensive_strength": offensive_strength / 2.0,
            }
        return opponent_data
  

def calculate_opponent_strength(team_id, opponent_data):
    """
    Calculate opponent strength by combining defensive and offensive strengths with recent form.
    """
    recent_form = TeamData.fetch_recent_form(team_id)
    opponent_strength = opponent_data.get(team_id, {}).get('defensive_strength', 0) + opponent_data.get(team_id, {}).get('offensive_strength', 0)
    
    return (opponent_strength + recent_form) / 2

    


from pulp import LpProblem, LpMaximize, LpVariable, LpStatus, lpSum

class TeamSelector:
   
    def __init__(self, players, total_budget, position_requirements, data, fixtures):
        self.players = players
        self.total_budget = total_budget
        self.position_requirements = position_requirements
        self.fixtures = fixtures
        self.data = data
        self.upcoming_fixture_difficulty = self.calculate_upcoming_fixture_difficulty()

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
    
    def normalize_fixture_difficulty(self):
        max_difficulty = max(self.upcoming_fixture_difficulty.values())
        min_difficulty = min(self.upcoming_fixture_difficulty.values())

        normalized_difficulty = {
            team: (difficulty - min_difficulty) / (max_difficulty - min_difficulty)
            for team, difficulty in self.upcoming_fixture_difficulty.items()
        }
        
        # Invert the normalized difficulty so that lower difficulty is better
        return {team: 1 - norm for team, norm in normalized_difficulty.items()}


    def select_team_lp(self):
        penalty_value = -100 

        self.upcoming_fixture_difficulty = self.normalize_fixture_difficulty()
        print('printed',self.upcoming_fixture_difficulty,self.position_requirements)
        
        # Assign meaningful weights for each position
        goalkeeper_weights = {
            "saves": 0.3,
            "clean_sheets": 0.4,
            "goals_conceded_per_90": 0.2,
            "bonus": 0.1,
            "fixture_difficulty": 0.5,
        }

        defender_weights = {
            "clean_sheets": 0.4,
            "goals_conceded_per_90": 0.3,
            "bonus": 0.2,
            "fixture_difficulty": 0.3,
        }

        midfielder_weights = {
            "expected_goals": 0.4,
            "expected_assists": 0.3,
            "expected_goal_involvements": 0.3,
            "ict_index": 0.3,
            "bonus": 0.3,
            "fixture_difficulty": 0.3,
        }

        forward_weights = {
            "expected_goals": 0.6,
            "expected_assists": 0.4,
            "expected_goal_involvements": 0.5,
            "ict_index": 0.3,
            "bonus": 0.2,
            "fixture_difficulty": 0.4,
        }

        prob = LpProblem("FPL_Team_Selection", LpMaximize)

        # Create binary variables for each player
        player_vars = {
            player['name']: LpVariable(player['name'], cat='Binary')
            for position in self.players for player in self.players[position]
        }

        # Constraint: exactly the required number of players in each position
        for position, required in self.position_requirements.items():
            prob += lpSum(
                player_vars[player['name']]
                for player in self.players[position]
            ) == required

        # Add premium player constraints
        premium_thresholds = {
            "goalkeepers": 5.0,
            "defenders": 6.0,
            "midfielders": 9.0,
            "forwards": 8.0
        }
        minimum_premium_players = {
            "goalkeepers": 1,
            "defenders": 2,
            "midfielders": 3,
            "forwards": 3
        }

        for position, min_premium in minimum_premium_players.items():
            prob += lpSum(
                player_vars[player['name']]
                for player in self.players[position]
                if player['price'] >= premium_thresholds[position]
            ) >= min_premium

        # Define the objective function with position-specific weights
        prob += lpSum(
            player_vars[player['name']] * (
                goalkeeper_weights['saves'] * float(player.get('saves_per_90', 0)) +
                goalkeeper_weights['clean_sheets'] * float(player.get('clean_sheets', 0)) +
                goalkeeper_weights['goals_conceded_per_90'] * (1 - float(player.get('goals_conceded_per_90', 0))) +
                goalkeeper_weights['bonus'] * float(player.get('bonus', 0)) +
                goalkeeper_weights['fixture_difficulty'] * (1 / self.upcoming_fixture_difficulty[player['team']])
                if player['position'] == 'goalkeepers' else 0 +
                
                defender_weights['clean_sheets'] * float(player.get('clean_sheets', 0)) +
                defender_weights['goals_conceded_per_90'] * (1 - float(player.get('goals_conceded_per_90', 0))) +
                defender_weights['bonus'] * float(player.get('bonus', 0)) +
                defender_weights['fixture_difficulty'] * (1 / self.upcoming_fixture_difficulty[player['team']])
                if player['position'] == 'defenders' else 0 +
                
                midfielder_weights['expected_goals'] * float(player.get('expected_goals', 0)) +
                midfielder_weights['expected_assists'] * float(player.get('expected_assists', 0)) +
                midfielder_weights['expected_goal_involvements'] * float(player.get('expected_goal_involvements', 0)) +
                midfielder_weights['ict_index'] * float(player.get('ict_index', 0)) +
                midfielder_weights['bonus'] * float(player.get('bonus', 0)) +
                midfielder_weights['fixture_difficulty'] * (1 / self.upcoming_fixture_difficulty[player['team']])
                if player['position'] == 'midfielders' else 0 +
                
                forward_weights['expected_goals'] * float(player.get('expected_goals', 0)) +
                forward_weights['expected_assists'] * float(player.get('expected_assists', 0)) +
                forward_weights['expected_goal_involvements'] * float(player.get('expected_goal_involvements', 0)) +
                forward_weights['ict_index'] * float(player.get('ict_index', 0)) +
                forward_weights['bonus'] * float(player.get('bonus', 0)) +
                forward_weights['fixture_difficulty'] * (1 / self.upcoming_fixture_difficulty[player['team']])
                if player['position'] == 'forwards' else 0
            )
            for position in self.players for player in self.players[position]
        )

                # Constraint: no more than 3 players from each club
        club_player_vars = {}
        for position in self.players:
            for player in self.players[position]:
                club_id = player['team']
                if club_id not in club_player_vars:
                    club_player_vars[club_id] = []
                club_player_vars[club_id].append(player_vars[player['name']])

        for club_id, club_vars in club_player_vars.items():
            prob += lpSum(club_vars) <= 3

        # Constraint: total price of selected players must be within the budget
        prob += lpSum(
            player_vars[player['name']] * player['price']
            for position in self.players for player in self.players[position]
        ) <= self.total_budget

        

        # Solve the problem
        prob.solve()

        # Check the status
        print("Solver Status:", LpStatus[prob.status])

        # Extract selected players
        team = {position: [] for position in self.position_requirements}
        for player_name, var in player_vars.items():
            if var.value() == 1:
                position = next(
                    (pos for pos in self.position_requirements 
                     if any(p['name'] == player_name for p in self.players[pos])
                    ), 
                    None
                )
                if position:
                    team[position].append(next(p for p in self.players[position] if p['name'] == player_name))
 


        return team

