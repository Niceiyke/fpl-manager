from player import PlayerParser
from strategy import TeamSelectorCP
from data import FPLDataFetcher



def create_and_manage_team():
    # Fetch data
    fpl_data = FPLDataFetcher.fetch_fpl_data()
    fixtures = FPLDataFetcher.fetch_fixtures()
    if not fpl_data or not fixtures:
        return

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


    team_selector_obj = TeamSelectorCP(players=players,
                                total_budget=total_budget,
                                position_requirements=position_requirements,
                                data=fpl_data,
                                fixtures=fixtures)
    
    team_selector=team_selector_obj.select_team_cp()

    if team_selector is None:
        
        print("Team selection failed due to a constraint violation or optimization issue.")
          # Handle the issue or exit the function
    else:
        total_price=0
        for position, players in team_selector.items():
            # Process the selected team
            print(f"Selected {len(players)} players for {position}:")
            for player in players:
                print(f"- {player['name']} -(${player['price']}M) -({player['points']}) -club:{player['team']}")
                total_price += player['price']
        print(f"\nTotal price of selected players: ${total_price:.1f}M")
        print(f"budget left: ${total_budget - total_price:.1f}M")


    # Run the main function
create_and_manage_team()