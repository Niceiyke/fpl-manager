from player import PlayerParser


async def  Parse_player_data(data,db):
    fixtures = await db.fetch_fixtures()
    parser = PlayerParser(data=data,fixtures=fixtures)
    return parser.players

async def  map_selected_picks(player_selections,db):
        players = await db.fetch_picks(player_selections)
        current_team = []
        for pick in player_selections:
            # Find the player with the matching id
            player = next((player for player in players if player["id"] == pick["element"]), None)
            if player:
                current_team.append(player)    
        return current_team