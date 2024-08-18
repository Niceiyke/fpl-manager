class EvaluatePlayer:

    def __init__(self,players) -> None:

        self.players = players
        
        self.calculate_max_values()
    
    def calculate_max_values(self):
            # Initialize max values
            self.max_clean_sheets = 0
            self.max_bonus = 0
            self.max_goals_conceded_per_90=0
            self.max_fdr = 0
            self.max_saves = 0
            self.max_expected_point = 0
            self.max_starts=0
            self.max_assists=0
            self.max_goals_scored=0
            self.max_expected_goals=0
            self.max_expected_assists=0
            self.max_ict_index = 0
            self.max_points_per_game=0
            self.form =0

            # Update max values based on players' data
            for position in self.players:
                for player in self.players[position]:
                    if position == "defenders":
                        self.max_clean_sheets = max(self.max_clean_sheets, int(float(player.get("clean_sheets", 0))))
                        self.max_bonus = max(self.max_bonus, int(float(player.get("bonus", 0))))
                        self.max_goals_conceded = max(self.max_goals_conceded, int(float(player.get("goals_conceded_per_90", 0))))
                        self.max_fdr = max(self.max_fdr, int(float(player.get("fixture_difficulty", 0))))
                        self.max_expected_point = max(self.max_expected_point, int(float(player.get("expected_point", 0))))
                        self.max_starts = max(self.max_starts, int(float(player.get("starts", 0))))
                        self.max_form = max(self.max_starts, int(float(player.get("form", 0))))
                        self.max_assists = max(self.max_assists, int(float(player.get("assists", 0))))
                        self.max_goals_scored = max(self.max_goals_scored, int(float(player.get("goals", 0))))
                        self.max_expected_assists = max(self.max_expected_assists, int(float(player.get("expected_assists", 0))))
                        self.max_expected_goals_scored = max(self.max_expected_goals, int(float(player.get("expected_goals", 0))))
                        
                        
                    elif position == "midfielders":
                        self.max_goals_scored = max(self.max_goals_scored, int(float(player.get("goals_scored", 0))))
                        self.max_bonus = max(self.max_bonus, int(float(player.get("bonus", 0))))
                        self.max_fdr = max(self.max_fdr, int(float(player.get("fixture_difficulty", 0))))
                        self.max_expected_point = max(self.max_expected_point, int(float(player.get("expected_point", 0))))
                        self.max_starts = max(self.max_starts, int(float(player.get("starts", 0))))
                        self.max_form = max(self.max_starts, int(float(player.get("form", 0))))
                        self.max_assists = max(self.max_assists, int(float(player.get("assists", 0))))
                        self.max_goals_scored = max(self.max_goals_scored, int(float(player.get("goals", 0))))
                        self.max_expected_assists = max(self.max_expected_assists, int(float(player.get("expected_assists", 0))))
                        self.max_expected_goals_scored = max(self.max_expected_goals, int(float(player.get("expected_goals", 0))))
                        

                    elif position == "forwards":
                        self.max_goals_scored = max(self.max_goals_scored, int(float(player.get("goals_scored", 0))))
                        self.max_bonus = max(self.max_bonus, int(float(player.get("bonus", 0))))
                        self.max_fdr = max(self.max_fdr, int(float(player.get("fixture_difficulty", 0))))
                        self.max_expected_point = max(self.max_expected_point, int(float(player.get("expected_point", 0))))
                        self.max_starts = max(self.max_starts, int(float(player.get("starts", 0))))
                        self.max_form = max(self.max_starts, int(float(player.get("form", 0))))
                        self.max_assists = max(self.max_assists, int(float(player.get("assists", 0))))
                        self.max_goals_scored = max(self.max_goals_scored, int(float(player.get("goals", 0))))
                        self.max_expected_assists = max(self.max_expected_assists, int(float(player.get("expected_assists", 0))))
                        self.max_expected_goals_scored = max(self.max_expected_goals, int(float(player.get("expected_goals", 0))))
                        
                        
                    elif position == "goalkeepers":
                        self.max_clean_sheets = max(self.max_clean_sheets, int(float(player.get("clean_sheets", 0))))
                        self.max_bonus = max(self.max_bonus, int(float(player.get("bonus", 0))))
                        self.max_goals_conceded = max(self.max_goals_conceded_per_90, int(float(player.get("goals_conceded_per_90", 0))))
                        self.max_fdr = max(self.max_fdr, int(float(player.get("fixture_difficulty", 0))))
                        self.max_saves = max(self.max_saves, int(float(player.get("saves", 0))))
                        self.max_expected_point = max(self.max_expected_point, int(float(player.get("expected_point", 0))))
                        self.max_starts = max(self.max_starts, int(float(player.get("starts", 0))))
                        self.max_form = max(self.max_starts, int(float(player.get("form", 0))))
  
 

    def evaluate_player(self, player,config):
        """
        Evaluate a player based on multiple metrics for selection and optimization,
        with adjustments based on the player's position and additional factors like 
        advanced metrics, rotation risk, form over time, and differential factor.
        """
        # Normalization of key metrics
       # Normalization of key metrics
        normalized_form = float(player["form"]) / self.max_form if self.max_form > 0 else 0
        normalized_expected_point = float(player["expected_point"]) / self.max_expected_point if self.max_expected_point > 0 else 0
        
        # Base score calculation
        base_score = (normalized_form * 0.4) + (normalized_expected_point * 0.6)
        
        # Position-specific contributions
        if player["position"] == 1:  # Goalkeeper
            defensive_contribution = (float(player["clean_sheets"]) / self.max_clean_sheets if self.max_clean_sheets > 0 else 0)
            final_score = base_score + defensive_contribution * 0.5
        
        elif player["position"] == 2:  # Defender
            offensive_contribution = (float(player["goals"]) / self.max_goals_scored if self.max_goals_scored > 0 else 0)
            defensive_contribution = (float(player["clean_sheets"]) / self.max_clean_sheets if self.max_clean_sheets > 0 else 0)
            final_score = base_score + offensive_contribution * 0.4 + defensive_contribution * 0.6

        elif player["position"] == 3:  # Midfielder
            offensive_contribution = (
                float(player["goals"]) / self.max_goals_scored if self.max_goals_scored > 0 else 0
                + float(player["assists"]) / self.max_assists if self.max_assists > 0 else 0
            )
            final_score = base_score + offensive_contribution * 0.8

        elif player["position"] == 4:  # Forward
            offensive_contribution = (
                float(player["goals"]) / self.max_goals_scored if self.max_goals_scored > 0 else 0
                + float(player["assists"]) / self.max_assists if self.max_assists > 0 else 0
            )
            final_score = base_score + offensive_contribution * 0.9

        # Introduce a floor to prevent negative scores
        final_score = max(final_score, 0)

        return final_score

        #if player["position"] ==3:
         #   print(f"{player['name']} - {player['team']} - {final_score}")

        return final_score
class PlayerParser:
    def __init__(self, data, fixtures):
        self.data = data
        self.fixtures = fixtures
        self.players = self.parse_players()

    def calculate_team_fixture_difficulty(self, team_id):
        num_upcoming_fixtures = 1
        team_fixtures = []
        
        for fixture in self.fixtures:
            if not fixture['finished']:
                if fixture['team_h'] == team_id:
                    team_fixtures.append(fixture['team_h_difficulty'])
                if fixture['team_a'] == team_id:
                    team_fixtures.append(fixture['team_a_difficulty'])

        upcoming_difficulties = team_fixtures[:num_upcoming_fixtures]
        
        if len(upcoming_difficulties) > 0:
            avg_difficulty = sum(upcoming_difficulties) / len(upcoming_difficulties)
        else:
            avg_difficulty = 0
        
        return avg_difficulty

    def parse_players(self):
        if not self.data or not self.fixtures:
            print("Data is missing or in an unexpected format.")
            return {}

        element_types = {1: "goalkeepers", 2: "defenders", 3: "midfielders", 4: "forwards"}
        players = {position: [] for position in element_types.values()}

        for player in self.data:
            position = element_types[player['element_type']]
            team_id = player['team']
            form = float(player['form'])
            fixture_difficulty = self.calculate_team_fixture_difficulty(team_id)

            players[position].append({
                "id": player['id'],
                "name": player['web_name'],
                "position": player['element_type'],
                "status": player['status'],
                "ict_index": player['ict_index'],
                "price": player['now_cost'] / 10,
                "total_points": player['total_points'],
                "goals": player['goals_scored'],
                "assists": player['assists'],
                "expected_goals": player['expected_goals'],
                "expected_assists": player['expected_assists'],
                "expected_goal_involvements": player['expected_goal_involvements'],
                "saves_per_90": player['saves_per_90'],
                "goals_conceded_per_90": player['goals_conceded_per_90'],
                "bonus": player['bonus'],
                "expected_point": player['ep_next'],
                "form": form,
                "fixture_difficulty": fixture_difficulty,
                "team": player['team'],
                "starts": player['starts'],
                "selected_by_percent": player['selected_by_percent'],
                "clean_sheets": player['clean_sheets'],
                "yellow_cards": player['yellow_cards'],
                "red_cards": player['red_cards'],
                "penalties_order": player['penalties_order'],
                "value_season": player['value_season'],
                
            })

        return players

    def calculate_upcoming_fixture_difficulty(self, num_weeks=5):
        team_fixtures = {team['id']: [] for team in self.data['teams']}
        
        for fixture in self.fixtures:
            if not fixture['finished']:
                home_team = fixture['team_h']
                away_team = fixture['team_a']
                
                if fixture['event'] <= num_weeks:
                    team_fixtures[home_team].append(fixture['team_h_difficulty'])
                    team_fixtures[away_team].append(fixture['team_a_difficulty'])

        avg_fixture_difficulty = {
            team_id: sum(difficulties) / len(difficulties) if len(difficulties) > 0 else 0
            for team_id, difficulties in team_fixtures.items()
        }

        return avg_fixture_difficulty

    
    