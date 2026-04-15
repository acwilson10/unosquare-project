from datetime import datetime
from typing import Optional
from app.strategies.route_strategy import BudgetResult, CostBreakdown


class CostCalculator:
    """
    CostCalculator — YOUR TASK #5

    ============================================================
    WHAT YOU NEED TO IMPLEMENT:
    ============================================================

    The calculate method should:
    1. Calculate ticket costs (sum of ticketPrice for all matches)
    2. Calculate flight costs (between consecutive cities + from origin)
    3. Calculate accommodation costs (nights × city's accommodationPerNight rate)
    4. Check feasibility (total ≤ budget AND visits USA, Mexico, Canada)
    5. Return suggestions if not feasible

    ============================================================
    HELPER METHODS PROVIDED:
    ============================================================

    The helper methods below are already implemented for you:
    - get_flight_price(): Look up flight price between two cities
    - calculate_nights_between(): Calculate nights between two dates
    - get_countries_visited(): Get list of unique countries from matches
    - get_missing_countries(): Check which required countries are missing
    - generate_suggestions(): Create cost-saving suggestions

    """

    REQUIRED_COUNTRIES = ['USA', 'Mexico', 'Canada']

    def calculate(
        self,
        matches: list,
        budget: float,
        origin_city_id: str,
        flight_prices: list
    ) -> BudgetResult:
        """
        Calculate the total cost of a trip and check if it's within budget.

        Args:
            matches: List of match dicts the user wants to attend (sorted by date)
            budget: The user's maximum budget in USD
            origin_city_id: The city where the user starts their trip
            flight_prices: All available flight prices between cities

        Returns:
            BudgetResult dict containing feasibility, costs, and suggestions
        """
        # TODO: Implement cost calculation (YOUR TASK #5)
        #
        # Pseudocode:
        # 1. Calculate ticket costs:
        #    - Sum of match['ticketPrice'] for all matches
        #
        # 2. Calculate flight costs:
        #    - From origin_city_id to first match's city
        #    - Between each consecutive match city (if different)
        #    - Use get_flight_price() helper to look up prices
        #
        # 3. Calculate accommodation costs:
        #    - For each city visited, calculate nights stayed
        #    - Use calculate_nights_between() for dates
        #    - Multiply nights by city's accommodationPerNight
        #
        # 4. Build CostBreakdown with all costs and total
        #
        # 5. Check country constraint:
        #    - Use get_countries_visited() and get_missing_countries()
        #    - If missing countries, set feasible = False
        #
        # 6. Check budget constraint:
        #    - If total > budget, set feasible = False
        #    - Set minimumBudgetRequired = total
        #
        # 7. Generate suggestions if not feasible:
        #    - Use generate_suggestions() helper
        #
        # 8. Return BudgetResult with all results

        if not matches:
            return {
                "feasible": False,
                "totalCost": 0,
                "breakdown": {},
                "missingCountries": self.REQUIRED_COUNTRIES,
                "suggestions": ["No matches selected"]
            }

        # Ensure matches are sorted by date
        matches = sorted(matches, key=lambda m: m['kickoff'])

        # 1. Calculate ticket costs:
        #    - Sum of match['ticketPrice'] for all matches
        ticket_cost = sum(match['ticketPrice'] for match in matches)

        # 2. Calculate flight costs:
        #    - From origin_city_id to first match's city
        #    - Between each consecutive match city (if different)
        #    - Use get_flight_price() helper to look up prices
        flight_cost = 0

        first_city_id = matches[0]['city']['id']
        flight_cost += self.get_flight_price(origin_city_id, first_city_id, flight_prices)

        for i in range(len(matches) - 1):
            current_city = matches[i]['city']['id']
            next_city = matches[i + 1]['city']['id']
            flight_cost += self.get_flight_price(current_city, next_city, flight_prices)

        # 3. Calculate accommodation costs:
        #    - For each city visited, calculate nights stayed
        #    - Use calculate_nights_between() for dates
        #    - Multiply nights by city's accommodationPerNight
        accommodation_cost = 0

        for i in range(len(matches) - 1):
            current_match = matches[i]
            next_match = matches[i + 1]

            nights = self.calculate_nights_between(
                current_match['kickoff'],
                next_match['kickoff']
            )

            rate = current_match['city']['accommodationPerNight']
            accommodation_cost += nights * rate

        # 4. Build CostBreakdown with all costs and total
        total_cost = ticket_cost + flight_cost + accommodation_cost

        breakdown: CostBreakdown = {
            "tickets": ticket_cost,
            "flights": flight_cost,
            "accommodation": accommodation_cost,
            "total": total_cost
        }

        # 5. Check country constraint:
        #    - Use get_countries_visited() and get_missing_countries()
        #    - If missing countries, set feasible = False
        countries_visited = self.get_countries_visited(matches)
        missing_countries = self.get_missing_countries(countries_visited)

        feasible = True
        if missing_countries:
            feasible = False

        # 6. Check budget constraint:
        #    - If total > budget, set feasible = False
        #    - Set minimumBudgetRequired = total
        minimum_budget_required: Optional[float] = None

        if total_cost > budget:
            feasible = False
            minimum_budget_required = total_cost

        # 7. Generate suggestions if not feasible:
        #    - Use generate_suggestions() helper
        suggestions = []
        if not feasible:
            suggestions = self.generate_suggestions(matches, total_cost, budget)

        # 8. Return BudgetResult with all results
        result: BudgetResult = {
            "feasible": feasible,
            "totalCost": total_cost,
            "breakdown": breakdown
        }

        if minimum_budget_required:
            result["minimumBudgetRequired"] = minimum_budget_required

        if missing_countries:
            result["missingCountries"] = missing_countries

        if suggestions:
            result["suggestions"] = suggestions

        return result
