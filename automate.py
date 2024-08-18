from auth import authenticate
from managemment import AutomatedTeamManagement
from player import PlayerParser,EvaluatePlayer
from config import FPLConfig
from data import FPLDataFetcher


def main():
    # Fetch data
    fpl_data = FPLDataFetcher.fetch_fpl_data()
    fixtures = FPLDataFetcher.fetch_fixtures()
    if not fpl_data or not fixtures:
        return
    data=fpl_data['elements']
    teams=fpl_data['teams']
    


    
   
    # Authenticate with FPL API
    my_info = authenticate()
  
    picks = my_info['picks']
    budget =float( my_info['transfers']['bank']/10 )
    free_transfers = my_info['transfers']['limit'] 
    team_value =float(my_info['transfers']['value']/10)
    print(f"budget:{budget} free_transfers:{free_transfers} team_value:{team_value}")



    # Manage the team
    team_management = AutomatedTeamManagement()
    
    team=team_management.map_selected_picks(picks,data )
    #print(f'Selected Picks: {team}')

    all_players_parse=PlayerParser(data,fixtures)
    all_players=all_players_parse.players

    # Parse and evaluate players
    player_parser = PlayerParser(team, fixtures)
    players = player_parser.players

    # Print the differential players
    differential_players =team_management.get_differential_players(all_players=data,all_teams=teams)

    diff_parser=PlayerParser(differential_players, fixtures)
    all_diff_players =diff_parser.players
     # Example logic for transferring out and finding replacements
    for position in players:
        for player in players[position]:
            replacements=team_management.transfer_tool(budget,all_diff_players,player)
                #budget_left = current_budget - player['cost']
            
            if (replacements)=='No transfer necessary':
                continue
            print(f"Transfer out:name:{player['name']} - price:{player['price']} - form:{player['form']} - Xp: {player['expected_point']} - club:{-player['team'] }")
            print("*"*10)
            print ("posible replacements:" )
            for r in replacements:
                    print(f"name: {r['name']} - price:{r['price']} -form:{r['form']} -Xp:{r['expected_point']} -club:{-r['team'] }")
            

  
    """


    best_lineup, bench =team_management.select_best_lineup_with_bench(players)

    print("Selected Lineup:")
    print(f"Goalkeeper: {[player['name'] for player in best_lineup['goalkeeper']]}")
    print("Defenders:", [player['name'] for player in best_lineup['defenders']])
    print("Midfielders:", [player['name'] for player in best_lineup['midfielders']])
    print("Forwards:", [player['name'] for player in best_lineup['forwards']])

    print("\nBench:")
    print("Bench Goalkeepers:", [player['name'] for player in bench['goalkeeper']] if bench['goalkeeper'] else 'None')
    print("Bench Defenders:", [player['name'] for player in bench['defenders']] if bench['defenders'] else 'None')
    print("Bench Midfielders:", [player['name'] for player in bench['midfielders']] if bench['midfielders'] else 'None')
    print("Bench Forwards:", [player['name'] for player in bench['forwards']] if bench['forwards'] else 'None')


    # Select captain and vice-captain
    captain, vice_captain =team_management.select_captain_and_vice(best_lineup)

    # Print the results
    print("Captain:", captain['name'])
    print("Vice-Captain:", vice_captain['name'])
            

    print("Top Differential Players (Under 10% Ownership):\n")
    print("Avaliable Differential players:",len( differential_players))
    for player in differential_players[:20]:  # Display top 10 differentials by form
        print(f"Name: {player['name']}, Team: {player['team']}, Position: {player['position']}, "
            f"Ownership: {player['ownership']}%, Form: {player['form']}, Total Points: {player['total_points']}, Price: {float(player['price'])/10}")
"""
    
    


main()


