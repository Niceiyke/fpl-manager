
from ortools.sat.python import cp_model

class TeamSelectorCP:
    goalkeeper_weights = {
    "saves": 1,
    "clean_sheets": 1,
    "goals_conceded_per_90": 1,
    "bonus": 1,
    "fixture_difficulty": 1,
}

    defender_weights = {
    "clean_sheets":1,
    "goals_scored": 1,
    "expected_assist": 1,
    "goals_conceded_per_90": 1,
    "bonus": 1,
    "fixture_difficulty": 1,
}

    midfielder_weights = {
            "expected_goals": 1,
            "expected_assists": 1,
            "expected_goal_involvements": 1,
            "ict_index": 1,
            "bonus": 1,
            "fixture_difficulty": 1,
        }

    forward_weights = {
            "expected_goals": 1,
            "expected_assists": 1,
            "expected_goal_involvements": 0,
            "ict_index": 1,
            "bonus": 1,
            "fixture_difficulty": 1,
        }
    # Map of position integers to position names
    position_map = {
            1: "goalkeepers",
            2: "defenders",
            3: "midfielders",
            4: "forwards"
        }

    def __init__(self, players, total_budget, position_requirements, data, fixtures):
        self.players = players
        self.total_budget = int(total_budget * 10)  # Scale the budget
        self.position_requirements = position_requirements
        self.data = data
        self.fixtures = fixtures
        self.upcoming_fixture_difficulty = self.calculate_upcoming_fixture_difficulty()
      
        self.calculate_max_values()
 
    
    def calculate_upcoming_fixture_difficulty(self, num_weeks=5):
        team_fixtures = {team["id"]: [] for team in self.data["teams"]}

        for fixture in self.fixtures:
            if not fixture["finished"]:
                home_team = fixture["team_h"]
                away_team = fixture["team_a"]

                # Only consider fixtures within the upcoming num_weeks
                if fixture["event"] <= num_weeks:
                    team_fixtures[home_team].append(fixture["team_h_difficulty"])
                    team_fixtures[away_team].append(fixture["team_a_difficulty"])

        avg_fixture_difficulty = {
            team_id: (
                sum(difficulties) / len(difficulties) if len(difficulties) > 0 else 0
            )
            for team_id, difficulties in team_fixtures.items()
        }

        return avg_fixture_difficulty
    
    def calculate_max_values(self):
        # Initialize max values
        self.max_clean_sheets = 0
        self.max_bonus = 0
        self.max_goals_conceded = 0
        self.max_fdr = 0
        self.max_goals_scored = 0
        self.max_assists = 0
        self.max_saves = 0
        self.max_expected_point=0

        # Update max values based on players' data
        for position in self.players:
            for player in self.players[position]:
                if position == "defenders":
                    self.max_clean_sheets = max(self.max_clean_sheets, int(player.get("clean_sheets", 0)))
                    self.max_bonus = max(self.max_bonus, int(player.get("bonus", 0)))
                    self.max_goals_conceded = max(self.max_goals_conceded, int(player.get("goals_conceded_per_90", 0)))
                    self.max_fdr = max(self.max_fdr, self.upcoming_fixture_difficulty.get(player["team"], 0))
                elif position == "midfielders":
                    self.max_goals_scored = max(self.max_goals_scored, int(player.get("goals_scored", 0)))
                    self.max_assists = max(self.max_assists, int(player.get("assists", 0)))
                    self.max_bonus = max(self.max_bonus, int(player.get("bonus", 0)))
                    self.max_fdr = max(self.max_fdr, self.upcoming_fixture_difficulty.get(player["team"], 0))
                elif position == "forwards":
                    self.max_goals_scored = max(self.max_goals_scored, int(player.get("goals_scored", 0)))
                    self.max_assists = max(self.max_assists, int(player.get("assists", 0)))
                    self.max_bonus = max(self.max_bonus, int(player.get("bonus", 0)))
                    self.max_fdr = max(self.max_fdr, self.upcoming_fixture_difficulty.get(player["team"], 0))
                if position == "goalkeepers":
                    self.max_clean_sheets = max(self.max_clean_sheets, int(player.get("clean_sheets", 0)))
                    self.max_bonus = max(self.max_bonus, int(player.get("bonus", 0)))
                    self.max_goals_conceded = max(self.max_goals_conceded, int(player.get("goals_conceded_per_90", 0)))
                    self.max_fdr = max(self.max_fdr, self.upcoming_fixture_difficulty.get(player["team"], 0))
                    self.max_saves = max(self.max_saves, int(player.get("saves", 0)))

    #Objective: maximize the total weighted score
    def get_player_score(self,player):
            pos = self.position_map[player["position"]]
            score = 0
            if pos == "goalkeepers":
                clean_sheets_score = (int(player.get("clean_sheets", 0)) / self.max_clean_sheets) if self.max_clean_sheets > 0 else 0
                bonus_score = (int(player.get("bonus", 0)) / self.max_bonus) if self.max_bonus > 0 else 0
                goals_conceded_score = (1 - (int(player.get("goals_conceded_per_90", 0)) / self.max_goals_conceded)) if self.max_goals_conceded > 0 else 0
                fdr_score = (1 - (self.upcoming_fixture_difficulty[player["team"]] / self.max_fdr)) if self.max_fdr > 0 else 0
                saves_score = (int(player.get("saves", 0)) / self.max_saves) if self.max_saves > 0 else 0
                expected_point=(int(player.get("expected_point", 0)) / self.max_saves) if self.max_saves > 0 else 0
                score = (
                    self.goalkeeper_weights["clean_sheets"] * clean_sheets_score
                    + self.goalkeeper_weights["bonus"] * bonus_score
                    + self.goalkeeper_weights["goals_conceded_per_90"] * goals_conceded_score
                    + self.goalkeeper_weights["fixture_difficulty"] * fdr_score
                    + self.goalkeeper_weights["saves"] * saves_score
                    + self.goalkeeper_weights["expected_point"]*expected_point
                )
            
            if pos == "defenders":
                clean_sheets_score = (int(player.get("clean_sheets", 0)) / self.max_clean_sheets) if self.max_clean_sheets > 0 else 0
                bonus_score = (int(player.get("bonus", 0)) / self.max_bonus) if self.max_bonus > 0 else 0
                goals_conceded_score = (1 - (int(player.get("goals_conceded_per_90", 0)) / self.max_goals_conceded)) if self.max_goals_conceded > 0 else 0
                fdr_score = (1 - (self.upcoming_fixture_difficulty[player["team"]] / self.max_fdr)) if self.max_fdr > 0 else 0
                expected_point=(int(player.get("expected_point", 0)) / self.max_saves) if self.max_saves > 0 else 0

                score = (
                    self.defender_weights["clean_sheets"] * clean_sheets_score
                    + self.defender_weights["bonus"] * bonus_score
                    + self.defender_weights["goals_conceded_per_90"] * goals_conceded_score
                    + self.defender_weights["fixture_difficulty"] * fdr_score
                    + self.defender_weights["expected_point"]*expected_point
                )

            elif pos == "midfielders":
                goals_scored_score = (int(player.get("goals_scored", 0)) / self.max_goals_scored) if self.max_goals_scored > 0 else 0
                assists_score = (int(player.get("assists", 0)) / self.max_assists) if self.max_assists > 0 else 0
                bonus_score = (int(player.get("bonus", 0)) / self.max_bonus) if self.max_bonus > 0 else 0
                fdr_score = (1 - (self.upcoming_fixture_difficulty[player["team"]] / self.max_fdr)) if self.max_fdr > 0 else 0
                expected_point=(int(player.get("expected_point", 0)) / self.max_saves) if self.max_saves > 0 else 0

                score = (
                    self.midfielder_weights["expected_goals"] * goals_scored_score
                    + self.midfielder_weights["expected_assists"] * assists_score
                    + self.midfielder_weights["bonus"] * bonus_score
                    + self.midfielder_weights["fixture_difficulty"] * fdr_score
                    + self.midfielder_weights["expected_point"]*expected_point
                )

            elif pos == "forwards":
                goals_scored_score = (int(player.get("goals_scored", 0)) / self.max_goals_scored) if self.max_goals_scored > 0 else 0
                assists_score = (int(player.get("assists", 0)) / self.max_assists) if self.max_assists > 0 else 0
                bonus_score = (int(player.get("bonus", 0)) / self.max_bonus) if self.max_bonus > 0 else 0
                fdr_score = (1 - (self.upcoming_fixture_difficulty[player["team"]] / self.max_fdr)) if self.max_fdr > 0 else 0
                expected_point=(int(player.get("expected_point", 0)) / self.max_saves) if self.max_saves > 0 else 0

                score = (
                    self.forward_weights["expected_goals"] * goals_scored_score
                    + self.forward_weights["expected_assists"] * assists_score
                    + self.forward_weights["bonus"] * bonus_score
                    + self.forward_weights["fixture_difficulty"] * fdr_score
                    + self.forward_weights["expected_point"]*expected_point
                )

            # Introduce a floor to prevent negative scores
            score = max(score, 0)
            
            if score > 0 :
                if pos =="forwards" :
                    print(f"Player: {player['name']}, Score: {score}")
            return score


    def select_team_cp(self):
        model = cp_model.CpModel()   
        # Create binary variables for each player
        player_vars = {
            player["name"]: model.NewBoolVar(player["name"])
            for position in self.players
            for player in self.players[position]
        }

        # Constraint: exactly the required number of players in each position
        for position, required in self.position_requirements.items():
            model.Add(
                sum(player_vars[player["name"]] for player in self.players[position])
                == required
            )

        # Constraint: no more than 3 players from each club
        club_player_vars = {}
        for position in self.players:
            for player in self.players[position]:
                club_id = player["team"]
                if club_id not in club_player_vars:
                    club_player_vars[club_id] = []
                club_player_vars[club_id].append(player_vars[player["name"]])

        for club_id, club_vars in club_player_vars.items():
            model.Add(sum(club_vars) <= 3)

        # Constraint: total price of selected players must be within the budget
        model.Add(
            sum(
                player_vars[player["name"]] * int(player["price"] * 10)  # Scale prices
                for position in self.players
                for player in self.players[position]
            )
            <= self.total_budget
        )

        #
        # Use `self.get_player_score` to call the method
        model.Maximize(
            sum(
                player_vars[player["name"]] * self.get_player_score(player)
                for position in self.players
                for player in self.players[position]
            )
        )

        # Solve the problem
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        # Check the status
        print("Solver Status:", solver.StatusName(status))

        # Extract selected players
        team = {position: [] for position in self.position_requirements}
        for player_name, var in player_vars.items():
            if solver.Value(var) == 1:
                position = next(
                    (
                        pos
                        for pos in self.position_requirements
                        if any(p["name"] == player_name for p in self.players[pos])
                    ),
                    None,
                )
                if position:
                    team[position].append(
                        next(
                            p
                            for p in self.players[position]
                            if p["name"] == player_name
                        )
                    )

        return team
