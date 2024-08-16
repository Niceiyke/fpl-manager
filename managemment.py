from player import PlayerScoreCalculator
from utility import RiskAssessor


class AutomatedTeamManagement:
    def __init__(self, picks,all_players):
        self.current_team = self.map_selected_picks(picks,all_players)
 
    def  map_selected_picks(self,picks,players):
        picked_players = []
        for pick in picks:
            # Find the player with the matching id
            player = next((player for player in players if player["id"] == pick["element"]), None)
            if player:
                picked_players.append(player)

        # Output the picked players
        #for player in picked_players:
            #print(player)
        
        return picked_players

    def transfer_decision(self, player_pool):
        transfers = []

        # Find players to transfer out (injured or underperforming)
        players_to_transfer_out = [
            player for position in self.current_team for player in self.current_team[position]
            if RiskAssessor.assess_injury_risk(player, self.injury_data) > 1 or player['form'] < 2
        ]

        # Identify replacement candidates for transfer
        for position in players_to_transfer_out:
            potential_replacements = sorted(
                player_pool[position],
                key=lambda p: PlayerScoreCalculator(self.injury_data, self.rotation_data, {}, {}).calculate_player_score(p, p['fixture_difficulty']),
                reverse=True
            )
            for player_out in players_to_transfer_out:
                for replacement in potential_replacements:
                    if replacement['price'] <= player_out['price'] + self.budget:
                        transfers.append((player_out, replacement))
                        self.budget -= (replacement['price'] - player_out['price'])
                        break

        return transfers

    def calculate_optimal_lineup(self):
        optimal_lineup = {position: [] for position in self.current_team}

        for position, players in self.current_team.items():
            # Sort players based on form and fixture difficulty
            players_sorted = sorted(players, key=lambda p: (p['form'], -p['fixture_difficulty']), reverse=True)
            if position == "goalkeepers":
                optimal_lineup[position] = players_sorted[:1]  # 1 starting goalkeeper
            else:
                optimal_lineup[position] = players_sorted[:4]  # Top 4 players in other positions

        return optimal_lineup

    def apply_transfers(self, transfers):
        for player_out, player_in in transfers:
            for position in self.current_team:
                if player_out in self.current_team[position]:
                    self.current_team[position].remove(player_out)
                    self.current_team[position].append(player_in)
                    break