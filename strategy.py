from pulp import LpMaximize, LpProblem, LpVariable, lpSum, LpStatus
from ortools.sat.python import cp_model

class TeamSelector:
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

    def __init__(self, players, total_budget, position_requirements, data, fixtures,evaluator,config):
        self.config=config
        self.evaluator=evaluator
        self.players = players
        self.total_budget = total_budget
        self.position_requirements = position_requirements
        self.fixtures = fixtures
        self.data = data
     

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
        model.Maximize(
            sum(
                player_vars[player["name"]] * self.evaluator(player)
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

        prob += lpSum(
            player_vars[player["name"]] * self.evaluator(player,self.config)
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

