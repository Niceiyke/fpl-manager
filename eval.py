
class EvalauatePlayer:

    def evaluate_player(self,player):
        """
        Evaluate a player based on multiple metrics for selection and optimization,
        with adjustments based on the player's position.
        """
        # Base score calculated using form, points per game, and expected points
        base_score = (float(player["form"]) + float(player["points_per_game"])) * float(player["ep_next"])

        # Availability check
        availability = 1 if player["status"] == "a" else 0.5  # Reduce score if not fully available

        # Position-specific metrics
        if player["element_type"] == 1:  # Goalkeeper
            offensive_contribution = 0  # No offensive contribution
            defensive_contribution = (
                float(player["clean_sheets"]) 
                + float(player["saves_per_90"]) 
                - float(player["goals_conceded_per_90"])
            )
        elif player["element_type"] == 2:  # Defender
            offensive_contribution = float(player["expected_goals"]) + float(player["expected_assists"])
            defensive_contribution = (
                float(player["clean_sheets"]) 
                + float(player["ict_index"])  # Adding ICT to defensive evaluation for defenders
                - float(player["goals_conceded_per_90"])
            )
        elif player["element_type"] == 3:  # Midfielder
            offensive_contribution = (
                float(player["expected_goals"]) 
                + float(player["expected_assists"]) 
                + float(player["ict_index"])  # ICT heavily influences midfielders' contribution
            )
            defensive_contribution = 0.5 * float(player["clean_sheets"])  # Midfielders contribute to defense, but less
        elif player["element_type"] == 4:  # Forward
            offensive_contribution = (
                float(player["expected_goals"]) 
                + float(player["expected_assists"]) 
                + 2 * float(player["ict_index"])  # Heavy emphasis on offensive metrics for forwards
            )
            defensive_contribution = 0  # No defensive contribution

        # Disciplinary impact
        disciplinary_impact = -0.5 * (player["yellow_cards"] + 2 * player["red_cards"])

        # Popularity and differential potential
        differential_factor = 1 if float(player["selected_by_percent"]) < 5 else 0.9  # Boost for low ownership

        # Cost efficiency
        cost_efficiency = float(player["value_season"]) / player["now_cost"]

        # Set-piece potential
        set_piece_potential = 1 if player["penalties_order"] is not None else 0.5

        # Final score calculation
        final_score = (
            base_score * availability
            + offensive_contribution
            + defensive_contribution
            + disciplinary_impact
            + differential_factor
            * cost_efficiency
            * set_piece_potential
        )

        return final_score

    
    def parse_injury_rotation_data(self,players):
        injury_data = {}
        rotation_data = {}

        # Iterate through each position and then each player within that position
        for position, player_list in players.items():
            for player in player_list:
                player_id = player['id']
                # Check if 'status' key exists before accessing it
                status = player.get('status', None)  # Use .get() to avoid KeyError
                # Similarly, check for 'news' key
                news = player.get('news', '')

                # Assess injury risk
                if status == 'i':
                    injury_data[player_id] = 2  # Major injury
                elif status == 'd':
                    injury_data[player_id] = 1  # Minor injury
                else:
                    injury_data[player_id] = 0  # No injury or status unknown

                # Assess rotation risk based on news or other factors
                if "rotation" in news.lower():
                    rotation_data[player_id] = 2  # High rotation risk
                elif "rested" in news.lower() or "doubtful" in news.lower():
                    rotation_data[player_id] = 1  # Moderate rotation risk
                else:
                    rotation_data[player_id] = 0  # No rotation risk

        return injury_data, rotation_data


