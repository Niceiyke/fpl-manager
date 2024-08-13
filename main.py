# Main function to create and manage a team
from data import FPLDataFetcher
from managemment import AutomatedTeamManagement
from player import PlayerParser,PlayerScoreCalculator
from team import TeamData, TeamSelector
from eval import EvalauatePlayer


def create_and_manage_team():
    # Fetch data
    fpl_data = FPLDataFetcher.fetch_fpl_data()
    fixtures = FPLDataFetcher.fetch_fixtures()
    if not fpl_data or not fixtures:
        return

    # Initialize objects
    team_data_list = fpl_data['teams']
    all_players =fpl_data['elements']
    team_data_obj=TeamData(team_data_list)
 
    opponent_data=team_data_obj.calculate_opponent_strengths()

    player_parser = PlayerParser(fpl_data, fixtures)
    players = player_parser.players
    team_data = {team['id']: team for team in team_data_list}

    # Team selection
    total_budget = 100  # Total budget in million
    position_requirements = {
        "goalkeepers": 2,
        "defenders": 5,
        "midfielders": 5,
        "forwards": 3
    }
    premium_thresholds = {
        "goalkeepers": 5.0,
        "defenders": 6.0,
        "midfielders": 8.0,
        "forwards": 9.0
    }
    minimum_premium_players = {
        "goalkeepers": 1,
        "defenders": 3,
        "midfielders": 2,
        "forwards": 2
    }

    eval_obj=EvalauatePlayer()

    injury_data, rotation_data =eval_obj.parse_injury_rotation_data(players)

    # Linear Programming approach
    team_selector_lp = TeamSelector(players, total_budget, position_requirements)
    selected_team_lp = team_selector_lp.select_team_lp()
    print("Selected team using Linear Programming:")
    for position, players in selected_team_lp.items():
        print(f"{position.capitalize()}:")
        for player in players:
            print(f"  - {player['name']} (${player['price']}m)")
    
  
    # Initialize Automated Team Management
    automated_management = AutomatedTeamManagement(selected_team_lp, total_budget, fixtures, injury_data, rotation_data)

    # Make transfer decisions
    transfers = automated_management.transfer_decision(players)
    print("\nTransfers:")
    for player_out, player_in in transfers:
        print(f"  - Out: {player_out['name']} (${player_out['price']}m), In: {player_in['name']} (${player_in['price']}m)")

    # Calculate optimal lineup
    optimal_lineup = automated_management.calculate_optimal_lineup()
    print("\nOptimal Lineup:")
    for position, lineup_players in optimal_lineup.items():
        print(f"{position.capitalize()}:")
        for player in lineup_players:
            print(f"  - {player['name']} (${(player['now_price']/10)}m)")


# Run the main function
create_and_manage_team()