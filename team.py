import heapq

import requests
from data import FIXTURES_API_URL
from player import PlayerScoreCalculator
from pulp import LpMaximize, LpProblem, LpVariable, lpSum

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

    
class TeamSelector:
    def __init__(self, players, total_budget, position_requirements):
        self.players = players
        self.total_budget = total_budget
        self.position_requirements = position_requirements

    def select_team_lp(self):
        prob = LpProblem("FPL_Team_Selection", LpMaximize)

        player_vars = {
            player['name']: LpVariable(player['name'], cat='Binary')
            for position in self.players for player in self.players[position]
        }

        # Define weights for predictive metrics
        predictive_weights = {
            "expected_goals": 0.5,
            "expected_assists": 0.3,
            "expected_goal_involvements": 0.2,
        }

        # Objective function: maximize the total weighted predictive score of the selected players
        prob += lpSum(player_vars[player['name']] * (
            predictive_weights['expected_goals'] * float(player['expected_goals']) +
            predictive_weights['expected_assists'] * float(player['expected_assists']) +
            predictive_weights['expected_goal_involvements'] * float(player['expected_goal_involvements'])
        )
            for position in self.players for player in self.players[position])

        # Constraint: total price of selected players must be within the budget
        prob += lpSum(player_vars[player['name']] * player['price']
                    for position in self.players for player in self.players[position]) <= self.total_budget

        # Constraint: exactly the required number of players in each position
        for position, required in self.position_requirements.items():
            prob += lpSum(player_vars[player['name']]
                        for player in self.players[position]) == required

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

        # Solve the problem
        prob.solve()

        # Extract selected players
        team = {position: [] for position in self.position_requirements}
        for player_name, var in player_vars.items():
            if var.value() == 1:
                position = next((pos for pos in self.position_requirements if any(p['name'] == player_name for p in self.players[pos])), None)
                if position:
                    team[position].append(next(p for p in self.players[position] if p['name'] == player_name))

        return team


    def select_team_greedy(self, premium_thresholds, minimum_premium_players, injury_data, rotation_data, team_data, opponent_data):
        team = {position: [] for position in self.position_requirements}
        remaining_budget = self.total_budget
        total_budget_used = 0
        club_per_position = {position: set() for position in team}

        # Create a priority queue for each position
        priority_queues = {position: [] for position in self.position_requirements}

        # Add players to the priority queues
        calculator = PlayerScoreCalculator(injury_data, rotation_data, team_data, opponent_data)
        for player in self.players:
            position = player["position"]  # Assuming each player dictionary has a 'position' key
            if position in priority_queues:
                score = calculator.calculate_player_score(player, player["fixture_difficulty"])
                heapq.heappush(priority_queues[position], (-score, player))

        # Select players from each priority queue based on scores
        for position, required_count in self.position_requirements.items():
            count_selected = 0
            premium_selected = 0
            premium_threshold = premium_thresholds.get(position, float('inf'))
            min_premium_required = minimum_premium_players.get(position, 0)

            while priority_queues[position] and count_selected < required_count:
                score, player = heapq.heappop(priority_queues[position])

                if premium_selected < min_premium_required and player["price"] < premium_threshold:
                    continue

                if player["price"] <= remaining_budget:
                    team[position].append(player)
                    remaining_budget -= player["price"]
                    total_budget_used += player["price"]
                    count_selected += 1
                    club_per_position[position].add(player["team"])
                    if player["price"] >= premium_threshold:
                        premium_selected += 1

                if count_selected == required_count:
                    break

        print(f"Total budget used: {total_budget_used}")
        print(f"Remaining budget: {remaining_budget}")
        return team

    
    def select_optimized_team(self,players, total_budget, position_requirements):
        """
        Select an optimized team based on enhanced player evaluation and user-defined strategies.
        """
        strategy = Strategy(risk_tolerance=2, preferred_formation=(1, 4, 4, 2))  # Example strategy
        team = {position: [] for position in position_requirements}
        remaining_budget = total_budget

        for position, num_required in position_requirements.items():
            eligible_players = [p for p in players if p["element_type"] == position_requirements[position]]
            ranked_players = sorted(
                eligible_players, key=lambda p:PlayerScoreCalculator.evaluate_player(p), reverse=True
            )

            for player in ranked_players:
                if (
                    player["now_cost"]/10 <= remaining_budget
                    and len(team[position]) < num_required
                ):
                    team[position].append(player)
                    remaining_budget -= player["now_cost"]/10

        return team
