# Main function to create and manage a team
from data import FPLDataFetcher
from player import PlayerParser
from team import TeamSelector
from cp import TeamSelectorCP



def create_and_manage_team():
    # Fetch data
    fpl_data = FPLDataFetcher.fetch_fpl_data()
    fixtures = FPLDataFetcher.fetch_fixtures()
    if not fpl_data or not fixtures:
        return

    # Initialize objects
    team_data_list = fpl_data['teams']

   

    player_parser = PlayerParser(fpl_data, fixtures)
    players = player_parser.players
   
    # Team selection
    total_budget = 100  # Total budget in million
    position_requirements = {
        "goalkeepers": 2,
        "defenders": 5,
        "midfielders": 5,
        "forwards": 3
    }
  
    # Linear Programming approach
    team_selector = TeamSelector(players, total_budget, position_requirements,fpl_data, fixtures)
    team_selector_cp = TeamSelectorCP(players, total_budget, position_requirements,fpl_data, fixtures)
    
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
                print(f"- {player['name']} -(${player['price']}M) -(${player['points']}) -club:{player['team']}")
                total_price += player['price']

    print(f"\nTotal price of selected players: ${total_price:.1f}M")
    print(f"budget left: ${total_budget - total_price:.1f}M")
        
    """
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
                print(f"- {player['name']} -(${player['price']}M) -({player['points']}) -club:{player['team']}")
                total_price += player['price']
        print(f"\nTotal price of selected players: ${total_price:.1f}M")
        print(f"budget left: ${total_budget - total_price:.1f}M")
    

    # Run the main function
create_and_manage_team()