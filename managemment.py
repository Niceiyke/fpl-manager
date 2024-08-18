import requests


class AutomatedTeamManagement:
    def __init__(self):
        
        self.current_team =[]
        self.expected_points_threshold=2

        
     

       
    def  map_selected_picks(self,picks,players):
        picked_players = []
        for pick in picks:
            # Find the player with the matching id
            player = next((player for player in players if player["id"] == pick["element"]), None)
            if player:
                picked_players.append(player)  
         
        self.current_team =picked_players    
        return picked_players
    

    def select_best_lineup_with_bench(self,players):
        # Function to sort and select players based on a weighted score
        def get_weighted_score(player):
            return (
                player['total_points'] * 0.5 +
                float(player['expected_goal_involvements']) * 0.3 -
                player['fixture_difficulty'] * 0.2
            )
        
        # Sort players in each position by their weighted score
        goalkeepers = sorted(players['goalkeepers'], key=get_weighted_score, reverse=True)
        defenders = sorted(players['defenders'], key=get_weighted_score, reverse=True)
        midfielders = sorted(players['midfielders'], key=get_weighted_score, reverse=True)
        forwards = sorted(players['forwards'], key=get_weighted_score, reverse=True)
        
        # Determine best formation based on the quality of players
        formations = [
            {'GK': 1, 'DEF': 3, 'MID': 4, 'FWD': 3},  # 3-4-3 formation
            {'GK': 1, 'DEF': 4, 'MID': 4, 'FWD': 2},  # 4-4-2 formation
            {'GK': 1, 'DEF': 3, 'MID': 5, 'FWD': 2},  # 3-5-2 formation
            {'GK': 1, 'DEF': 4, 'MID': 3, 'FWD': 3},  # 4-3-3 formation
            {'GK': 1, 'DEF': 5, 'MID': 3, 'FWD': 2},  # 5-3-2 formation
        ]
        
        best_lineup = None
        best_score = -float('inf')
        
        for formation in formations:
            lineup = {
                'goalkeeper': goalkeepers[:formation['GK']],
                'defenders': defenders[:formation['DEF']],
                'midfielders': midfielders[:formation['MID']],
                'forwards': forwards[:formation['FWD']],
            }
            
            # Calculate the total score for this lineup
            total_score = (
                sum(get_weighted_score(player) for player in lineup['goalkeeper']) +
                sum(get_weighted_score(player) for player in lineup['defenders']) +
                sum(get_weighted_score(player) for player in lineup['midfielders']) +
                sum(get_weighted_score(player) for player in lineup['forwards'])
            )
            
            if total_score > best_score:
                best_lineup = lineup
                best_score = total_score
        
        # Ensure we are not selecting starting players again for the bench
        remaining_goalkeepers = [player for player in goalkeepers if player not in best_lineup['goalkeeper']]
        remaining_defenders = [player for player in defenders if player not in best_lineup['defenders']]
        remaining_midfielders = [player for player in midfielders if player not in best_lineup['midfielders']]
        remaining_forwards = [player for player in forwards if player not in best_lineup['forwards']]
        
        # Select bench players: 1 GK, 1 DEF, 1 MID, 1 FWD
        bench = {
    'goalkeepers': remaining_goalkeepers[:1],  # 1 GK on the bench
    'defenders': remaining_defenders[:3],  # Up to 3 DEFs on the bench
    'midfielders': remaining_midfielders[:3],  # Up to 3 MIDs on the bench
    'forwards': remaining_forwards[:3],  # Up to 3 FWDs on the bench
}

        # Combine bench positions into a single list and trim to ensure the total squad size is 15
        bench_combined = bench['goalkeepers'] + bench['defenders'] + bench['midfielders'] + bench['forwards']
        bench_combined = bench_combined[:4]  # Ensuring exactly 4 bench players to maintain the 15-player squad

        bench = {
            'goalkeeper': [player for player in bench_combined if player['position'] == 1],
            'defenders': [player for player in bench_combined if player['position'] == 2],
            'midfielders': [player for player in bench_combined if player['position'] == 3],
            'forwards': [player for player in bench_combined if player['position'] == 4],
        }
        return best_lineup, bench

    def select_captain_and_vice(self,best_lineup):
        # Combine all players into one list
        all_players = (
            best_lineup['goalkeeper'] +
            best_lineup['defenders'] +
            best_lineup['midfielders'] +
            best_lineup['forwards']
        )
        
        # Convert 'expected_point' to float for comparison
        for player in all_players:
            player['expected_point'] = float(player['expected_point'])
            player['fixture_difficulty'] = float(player['fixture_difficulty'])
        
        # Sort players by a weighted combination of ICT index, expected points, and fixture difficulty
        # Higher ICT index and expected points are better, lower fixture difficulty is better
        sorted_players = sorted(all_players, key=lambda x: (
            float(x['ict_index']) * 0.5 + 
            x['expected_point'] * 0.3 - 
            x['fixture_difficulty'] * 0.2
        ), reverse=True)
        
        if len(sorted_players) < 2:
            raise ValueError("Not enough players to select captain and vice-captain.")
        
        # Select the top player as captain
        captain = sorted_players[0]
        
        # Select the second top player as vice-captain
        vice_captain = sorted_players[1]
        
        return captain, vice_captain
    
    def should_transfer_out(self, player):
        try:
            form = float(player['form'])
            expected_points = float(player['expected_point'])
            status = player['status']
            difficulty =float(player['fixture_difficulty'])
        except ValueError:
            return False
        
        player['name']

        # Dynamic threshold adjustment based on upcoming fixtures' difficulty
        dynamic_form_threshold = form * 1/difficulty
        
        
        # Transfer out criteria
        return form < 2

    def find_replacement_candidates(self, players_pool, budget, outgoing_player):
        candidates = []
        outgoing_position = outgoing_player['position']
        outgoing_price = float(outgoing_player['price'])

        for pos in players_pool:
            for player in players_pool[pos]:
                if player['position']== outgoing_position:
                    try:
                        price = float(player['price'])
                    except ValueError:
                        continue

                    if price <= budget + outgoing_price:
                        candidates.append(player)
                       
        
        return candidates

    def evaluate_replacements(self, candidates):
        for player in candidates:
            try:
                player['expected_point'] = float(player['expected_point'])
            except ValueError:
                player['expected_point'] = 0.0

            # Adding weighted scoring
            
            player['weighted_score'] = (player['expected_point'] * 0.7) - (player['fixture_difficulty'] * 0.3)
        
        return sorted(candidates, key=lambda x: x['weighted_score'], reverse=True)[:5]

    def transfer_tool(self, current_budget, players_pool, outgoing_player):
        
        if self.should_transfer_out(outgoing_player):
            replacement_candidates = self.find_replacement_candidates(players_pool, current_budget, outgoing_player)
            best_replacements = self.evaluate_replacements(replacement_candidates)
            return best_replacements
        else:
            return "No transfer necessary"
        
    # Identify differential players
    def get_differential_players(self,all_players,all_teams,min_games_played=1, max_ownership=10): 
        teams = {team['id']: team['name'] for team in all_teams}
        positions = {position['id'] for position in all_players}

        differential_players = []

        for player in all_players:
            ownership = float(player['selected_by_percent'])
            games_played = player['minutes'] / 90

            if ownership < max_ownership and games_played >= min_games_played:
                differential_players.append(player)

        return sorted(differential_players, key=lambda x: x['form'], reverse=True)

