# Main function to create and manage a team
from config import FPLConfig
from data import FPLDataFetcher
from player import PlayerParser,EvaluatePlayer
from team import TeamSelector
from cp import TeamSelectorCP



def create_and_manage_team():
    # Fetch data
    fpl_data = FPLDataFetcher.fetch_fpl_data()
    fixtures = FPLDataFetcher.fetch_fixtures()
    if not fpl_data or not fixtures:
        return

    player_parser = PlayerParser(fpl_data, fixtures)
    players = player_parser.players
    config = config = FPLConfig(
    availability_weight=1.0,
    differential_thresholds={5: 1, 20: 1, 100: 1},
    cost_efficiency_weight=1.2,
    set_piece_weight=1.0,
    fdr_weight=2.0,
    recent_form_weight=5.0,
    rotation_risk_weight=0.8,
    team_strength_weight=1.0,
    xg_xa_weight=1.5
)
    evaluate_player_obj=EvaluatePlayer(players)
    evaluator=evaluate_player_obj.evaluate_player
   
    # Team selection
    total_budget = 100  # Total budget in million
    position_requirements = {
        "goalkeepers": 2,
        "defenders": 5,
        "midfielders": 5,
        "forwards": 3
    }
  
    # Linear Programming approach
    team_selector = TeamSelector(players, total_budget, position_requirements,fpl_data, fixtures,evaluator,config)
    team_selector_cp = TeamSelectorCP(players, total_budget, position_requirements,fpl_data, fixtures,evaluator,config)
    """
    selected_team_lp = team_selector.select_team_lp()
    if selected_team_lp is None:
        
        print("Team selection failed due to a constraint violation or optimization issue.")
          # Handle the issue or exit the function
    else:
        total_price=0
        for position, players in selected_team_lp.items():
            # Process the selected team
            print(f"Selected {len(players)} players for {position}:")
            for player in players:
                print(f"- {player['name']} -(${player['price']}M)  -club:{player['team']}")
                total_price += player['price']

    print(f"\nTotal price of selected players: ${total_price:.1f}M")
    print(f"budget left: ${total_budget - total_price:.1f}M")
        
    
    selected_team_ga = team_selector.select_team_ga()
    if selected_team_ga is None:
        
        print("Team selection failed due to a constraint violation or optimization issue.")
          # Handle the issue or exit the function
    else:
        # Initialize total price
        total_price = 0

        # Print the name and price of each player
        print("Selected Team:")
        for player in selected_team_ga:
            name = player['name']
            price = player['price']
            total_price += price
            print(f"Name: {name}, Price: {price:.1f}")

        # Print the total price of the team
        print(f"\nTotal Price of the Team: {total_price:.1f}")

    print(f"\nTotal price of selected players: ${total_price:.1f}M")
    print(f"budget left: ${total_budget - total_price:.1f}M")
    """

    selected_team_c=team_selector_cp.select_team_cp()

    if selected_team_c is None:
        
        print("Team selection failed due to a constraint violation or optimization issue.")
          # Handle the issue or exit the function
    else:
        total_price=0
        for position, players in selected_team_c.items():
            # Process the selected team
            print(f"Selected {len(players)} players for {position}:")
            for player in players:
                print(f"- {player['name']} -(${player['price']}M)  -club:{player['team']}")
                total_price += player['price']
        print(f"\nTotal price of selected players: ${total_price:.1f}M")
        print(f"budget left: ${total_budget - total_price:.1f}M")
    


# Run the main function
create_and_manage_team()