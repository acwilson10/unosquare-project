from app.strategies.route_strategy import RouteStrategy, build_route
from app.utils.haversine import calculate_distance


class NearestNeighbourStrategy(RouteStrategy):
    """
    NearestNeighbourStrategy — YOUR TASK #3

    Implement a smarter route optimisation using the nearest-neighbour heuristic.
    The idea: when you have multiple matches on the same day (or close dates),
    choose the one that's geographically closest to where you currently are.

    This should produce shorter total distances than DateOnlyStrategy.
    """

    def optimise(self, matches: list) -> dict:
        if not matches:
            return build_route([], 'nearest-neighbour')

        # 1. Sort all matches by kickoff date
        sorted_matches = sorted(matches, key=lambda m: m['kickoff'])

        # 2. Group matches that fall on the same day
        # Hint: match['kickoff'].split('T')[0] gives the date string
        grouped_by_date = {}
        for match in sorted_matches:
            date = match['kickoff'].split('T')[0]
            grouped_by_date.setdefault(date, []).append(match)

        ordered_matches = []

        # 3. Start with the first match chronologically — this is your starting city
        first_date = sorted(grouped_by_date.keys())[0]
        first_match = grouped_by_date[first_date][0]

        ordered_matches.append(first_match)

        current_city = first_match['city']

        # 4. For each subsequent day group:
        for date in sorted(grouped_by_date.keys())[1:]:
            matches_on_day = grouped_by_date[date]

            # a. If only one match that day → add it to the route
            if len(matches_on_day) == 1:
                chosen_match = matches_on_day[0]

            else:
                # b. If multiple matches that day → pick the one whose city is closest
                min_distance = float('inf')
                chosen_match = None

                for candidate in matches_on_day:
                    dist = calculate_distance(
                        current_city['latitude'],
                        current_city['longitude'],
                        candidate['city']['latitude'],
                        candidate['city']['longitude']
                    )

                    if dist < min_distance:
                        min_distance = dist
                        chosen_match = candidate

            # Add chosen match to route
            ordered_matches.append(chosen_match)

            # 5. Track your "current city" as you go — update it after each match
            current_city = chosen_match['city']

        # 6. Return build_route(ordered_matches, 'nearest-neighbour')
        return build_route(ordered_matches, 'nearest-neighbour')
