import random
from pulp import LpMaximize, LpProblem, LpVariable, lpSum, LpStatus
from deap import base, creator, tools, algorithms
from ortools.sat.python import cp_model

class TeamSelector:
    position_map = {
        1: 'goalkeepers',
        2: 'defenders',
        3: 'midfielders',
        4: 'forwards'
    }

    goalkeeper_weights = {
            "saves": 0,
            "clean_sheets": 0.3,
            "goals_conceded_per_90": 0.3,
            "bonus": 0.3,
            "fixture_difficulty": 0.3,
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
            "ict_index": 1.3,
            "bonus": 1.3,
            "fixture_difficulty": 1.3,
        }

    forward_weights = {
            "expected_goals": 1.6,
            "expected_assists": 1.4,
            "expected_goal_involvements": 1.5,
            "ict_index": 1.3,
            "bonus": 1.2,
            "fixture_difficulty": 1.4,
        }
        # Add premium player constraints
    premium_thresholds = {
            "goalkeepers": 6.0,
            "defenders": 7.0,
            "midfielders": 10.0,
            "forwards": 8.0,
        }
    minimum_premium_players = {
            "goalkeepers": 1,
            "defenders": 2,
            "midfielders": 3,
            "forwards": 2,
        }

    def __init__(self, players, total_budget, position_requirements, data, fixtures):
        self.players = players
        self.total_budget = total_budget
        self.position_requirements = position_requirements
        self.fixtures = fixtures
        self.data = data
        self.upcoming_fixture_difficulty = self.calculate_upcoming_fixture_difficulty()

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

    def evaluate_team(self, individual):
        total_cost = 0
        total_score = 0

        team = {position: [] for position in self.position_requirements}
        for i, selected in enumerate(individual):
            if selected == 1:
                player = self.all_players[i]
                # Map integer position to string
                position = self.position_map[player["position"]]
                team[position].append(player)
                total_cost += player["price"]
                total_score += self.calculate_player_score(player)

        # Penalty if the team is over budget or doesn't meet the requirements
        penalty = 0
        if total_cost > self.total_budget:
            penalty += (total_cost - self.total_budget) * 10

        for position, players in team.items():
            required = self.position_requirements[position]
            if len(players) != required:
                penalty += abs(len(players) - required) * 100

        return total_score - penalty,

    def calculate_player_score(self, player):
        # Implement your scoring function based on player stats and fixture difficulty
        position = self.position_map[player["position"]]
        if position == "goalkeepers":
            weights = self.goalkeeper_weights
        elif position == "defenders":
            weights = self.defender_weights
        elif position == "midfielders":
            weights = self.midfielder_weights
        elif position == "forwards":
            weights = self.forward_weights
        else:
            return 0  # Default to 0 if position is not recognized

        # Calculate the player's score based on their stats and the assigned weights
        score = 0
        if position == "goalkeepers":
            score += (
                weights["saves"] * float(player.get("saves_per_90", 0))
                + weights["clean_sheets"] * float(player.get("clean_sheets", 0))
                + weights["goals_conceded_per_90"] * (1 - float(player.get("goals_conceded_per_90", 0)))
                + weights["bonus"] * float(player.get("bonus", 0))
                + weights["fixture_difficulty"] * (1 / self.upcoming_fixture_difficulty[player["team"]])
            )
        elif position == "defenders":
            score += (
                weights["clean_sheets"] * float(player.get("clean_sheets", 0))
                + weights["goals_conceded_per_90"] * (1 - float(player.get("goals_conceded_per_90", 0)))
                + weights["bonus"] * float(player.get("bonus", 0))
                + weights["fixture_difficulty"] * (1 / self.upcoming_fixture_difficulty[player["team"]])
            )
        elif position == "midfielders":
            score += (
                weights["expected_goals"] * float(player.get("expected_goals", 0))
                + weights["expected_assists"] * float(player.get("expected_assists", 0))
                + weights["expected_goal_involvements"] * float(player.get("expected_goal_involvements", 0))
                + weights["ict_index"] * float(player.get("ict_index", 0))
                + weights["bonus"] * float(player.get("bonus", 0))
                + weights["fixture_difficulty"] * (1 / self.upcoming_fixture_difficulty[player["team"]])
            )
        elif position == "forwards":
            score += (
                weights["expected_goals"] * float(player.get("expected_goals", 0))
                + weights["expected_assists"] * float(player.get("expected_assists", 0))
                + weights["expected_goal_involvements"] * float(player.get("expected_goal_involvements", 0))
                + weights["ict_index"] * float(player.get("ict_index", 0))
                + weights["bonus"] * float(player.get("bonus", 0))
                + weights["fixture_difficulty"] * (1 / self.upcoming_fixture_difficulty[player["team"]])
            )

        return score
        pass

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
                player_vars[player["name"]] *int( player["price"]*10)
                for position in self.players
                for player in self.players[position]
            )
            <= self.total_budget
        )

        # Objective: maximize the total weighted score
        def get_player_score(player):
            pos = player["position"]
           
            
            score = (
                 self.goalkeeper_weights["saves"] * int(player.get("saves_per_90", 0)*10)
                    + self.goalkeeper_weights["clean_sheets"]
                    * int(player.get("clean_sheets", 0)*10)
                    + self.goalkeeper_weights["goals_conceded_per_90"]
                    * (1 - int(player.get("goals_conceded_per_90", 0))*10)
                    + self.goalkeeper_weights["bonus"] * int(player.get("bonus", 0)*10)
                    + self.goalkeeper_weights["fixture_difficulty"]
                    * (1 / self.upcoming_fixture_difficulty[player["team"]])*10
            )
            return score

        model.Maximize(
            sum(
                player_vars[player["name"]] * get_player_score(player)
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

    def select_team_lp(self):
        # Assign meaningful weights for each position
        prob = LpProblem("FPL_Team_Selection", LpMaximize)

        # Create binary variables for each player
        player_vars = {
            player["name"]: LpVariable(player["name"], cat="Binary")
            for position in self.players
            for player in self.players[position]
        }

        # Constraint: exactly the required number of players in each position
        for position, required in self.position_requirements.items():
            prob += (
                lpSum(player_vars[player["name"]] for player in self.players[position])
                == required
            )

        position_map = {
            1: "goalkeepers",
            2: "defenders",
            3: "midfielders",
            4: "forwards",
        }
       

        # Update the objective function
        prob += lpSum(
            player_vars[player["name"]]
            * (
                # Weight calculation for goalkeepers
                (
                    self.goalkeeper_weights["saves"] * float(player.get("saves_per_90", 0))
                    + self.goalkeeper_weights["clean_sheets"]
                    * float(player.get("clean_sheets", 0))
                    + self.goalkeeper_weights["goals_conceded_per_90"]
                    * (1 - float(player.get("goals_conceded_per_90", 0)))
                    + self.goalkeeper_weights["bonus"] * float(player.get("bonus", 0))
                    + self.goalkeeper_weights["fixture_difficulty"]
                    * (1 / self.upcoming_fixture_difficulty[player["team"]])
                )
                if position_map[player["position"]] == "goalkeepers"
                else (
                    0 +
                    # Weight calculation for defenders
                    (
                        self.defender_weights["clean_sheets"]
                        * float(player.get("clean_sheets", 0))
                        + self.defender_weights["goals_conceded_per_90"]
                        * (1 - float(player.get("goals_conceded_per_90", 0)))
                        + self.defender_weights["bonus"] * float(player.get("bonus", 0))
                        + self.defender_weights["fixture_difficulty"]
                        * (1 / self.upcoming_fixture_difficulty[player["team"]])
                    )
                    if position_map[player["position"]] == "defenders"
                    else (
                        0 +
                        # Weight calculation for midfielders
                        (
                            self.midfielder_weights["expected_goals"]
                            * float(player.get("expected_goals", 0))
                            + self.midfielder_weights["expected_assists"]
                            * float(player.get("expected_assists", 0))
                            + self.midfielder_weights["expected_goal_involvements"]
                            * float(player.get("expected_goal_involvements", 0))
                            + self.midfielder_weights["ict_index"]
                            * float(player.get("ict_index", 0))
                            + self.midfielder_weights["bonus"]
                            * float(player.get("bonus", 0))
                            + self.midfielder_weights["fixture_difficulty"]
                            * (1 / self.upcoming_fixture_difficulty[player["team"]])
                        )
                        if position_map[player["position"]] == "midfielders"
                        else (
                            0 +
                            # Weight calculation for forwards
                           
                            (
                                self.forward_weights["expected_goals"]
                                * float(player.get("expected_goals", 0))
                                + self.forward_weights["expected_assists"]
                                * float(player.get("expected_assists", 0))
                                + self.forward_weights["expected_goal_involvements"]
                                * float(player.get("expected_goal_involvements", 0))
                                + self.forward_weights["ict_index"]
                                * float(player.get("ict_index", 0))
                                + self.forward_weights["bonus"]
                                * float(player.get("bonus", 0))
                                + self.forward_weights["fixture_difficulty"]
                                * (1 / self.upcoming_fixture_difficulty[player["team"]])
                            )
                            if position_map[player["position"]] == "forwards"
                            else 0
                        )
                    )
                )
            )
            for pos in self.players
            for player in self.players[pos]
        )
                # Update premium player constraints
        for pos, min_premium in self.minimum_premium_players.items():
          
            prob += (
                lpSum(
                    player_vars[player["name"]]
                    for player in self.players[position]
                    if player["price"] >= self.premium_thresholds[position]
                )
                >= min_premium
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
            prob += lpSum(club_vars) <= 3

        # Constraint: total price of selected players must be within the budget
        prob += (
            lpSum(
                player_vars[player["name"]] * player["price"]
                for position in self.players
                for player in self.players[position]
            )
            <= self.total_budget
        )

        # Optionally: Add a penalty for higher prices to encourage budget-friendly choices
        price_penalty_factor = 0.1
        prob += lpSum(
            player_vars[player["name"]] * price_penalty_factor * player["price"]
            for position in self.players
            for player in self.players[position]
        )

        # Solve the problem
        prob.solve()

        # Check the status
        print("Solver Status:", LpStatus[prob.status])

        # Extract selected players
        team = {position: [] for position in self.position_requirements}
        for player_name, var in player_vars.items():
            if var.value() == 1:
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

    def select_team_ga(self):
            # Flatten all players into a list
            self.all_players = []
            for position in self.players:
                self.all_players.extend(self.players[position])

            creator.create("FitnessMax", base.Fitness, weights=(1.0,))
            creator.create("Individual", list, fitness=creator.FitnessMax)

            toolbox = base.Toolbox()
            toolbox.register("attr_bool", random.randint, 0, 1)
            toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, n=len(self.all_players))
            toolbox.register("population", tools.initRepeat, list, toolbox.individual)

            toolbox.register("mate", tools.cxTwoPoint)
            toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
            toolbox.register("select", tools.selTournament, tournsize=3)
            toolbox.register("evaluate", self.evaluate_team)

            population = toolbox.population(n=300)
            algorithms.eaSimple(population, toolbox, cxpb=0.5, mutpb=0.2, ngen=50, verbose=False)

            # Select the best individual
            best_individual = tools.selBest(population, k=1)[0]

            selected_team = []
            for i, selected in enumerate(best_individual):
                if selected == 1:
                    selected_team.append(self.all_players[i])

            return selected_team