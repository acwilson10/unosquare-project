from flask import Blueprint, jsonify, request
from app.models.match import Match
from app.models.flight_price import FlightPrice
from app.strategies.nearest_neighbour_strategy import NearestNeighbourStrategy
# Tip: You can also import DateOnlyStrategy to compare results
from app.strategies.date_only_strategy import DateOnlyStrategy

optimise_bp = Blueprint('optimise', __name__)

# ============================================================
#  Route Optimisation — YOUR TASK #3 and #5
#
#  Implement route optimisation and budget calculation endpoints.
# ============================================================


# ============================================================
#  POST /api/route/optimise — Optimise a travel route
# ============================================================
#
# TODO: Implement this endpoint (YOUR TASK #3)
#
# Request body: { "matchIds": ["match-1", "match-5", "match-12", ...] }
#
# Steps:
#   1. Extract matchIds from the request JSON
#   2. Fetch full match data from the database
#   3. Convert matches to dicts (using match.to_dict())
#   4. Create a strategy instance: NearestNeighbourStrategy()
#      (or DateOnlyStrategy() to test with the working example first)
#   5. Call strategy.optimise(match_dicts)
#   6. Return the optimised route as JSON
#
# TIP: Start by using DateOnlyStrategy to verify your endpoint works,
# then switch to NearestNeighbourStrategy once you've implemented it.
#
# ============================================================

@optimise_bp.route('/optimise', methods=['POST'])
def optimise():
    # 1. Extract matchIds from the request JSON
    data = request.get_json()
    match_ids = data.get('matchIds')

    # Basic validation
    if not match_ids or not isinstance(match_ids, list):
        return jsonify({"error": "matchIds must be a non-empty list"}), 400

    # 2. Fetch full match data from the database
    matches = Match.query.filter(Match.id.in_(match_ids)).all()

    if not matches:
        return jsonify({"error": "No matches found for given IDs"}), 404

    # 3. Convert matches to dicts (using match.to_dict())
    match_dicts = [match.to_dict() for match in matches]

    # 4. Create a strategy instance: NearestNeighbourStrategy()
    # (or DateOnlyStrategy() to test with the working example first)
    strategy = NearestNeighbourStrategy()

    # strategy = DateOnlyStrategy()

    # 5. Call strategy.optimise(match_dicts)
    optimised_route = strategy.optimise(match_dicts)

    # 6. Return the optimised route as JSON
    return jsonify(optimised_route), 200


# ============================================================
#  POST /api/route/budget — Calculate trip costs and check budget
# ============================================================
#
# TODO: Implement this endpoint (YOUR TASK #5)
#
# Request body:
# {
#   "budget": 5000.00,
#   "matchIds": ["match-1", "match-5", "match-12", ...],
#   "originCityId": "city-atlanta"
# }
#
# Steps:
#   1. Extract budget, matchIds, and originCityId from request JSON
#   2. Fetch matches by IDs from the database
#   3. Convert matches to dicts (using match.to_dict())
#   4. Fetch all flight prices from the database
#   5. Create a CostCalculator instance
#   6. Call calculator.calculate(match_dicts, budget, origin_city_id, flight_prices)
#   7. Return the BudgetResult as JSON
#
# IMPORTANT CONSTRAINTS:
#   - User MUST attend at least 1 match in each country (USA, Mexico, Canada)
#   - If the budget is insufficient, return feasible=False with:
#     - minimumBudgetRequired: the actual cost
#     - suggestions: ways to reduce cost
#   - If countries are missing, return feasible=False with:
#     - missingCountries: list of countries not covered
#
# ============================================================

@optimise_bp.route('/budget', methods=['POST'])
def budget_optimise():

    # 1. Extract budget, matchIds, and originCityId from request JSON
    data = request.get_json()

    budget = data.get('budget')
    match_ids = data.get('matchIds')
    origin_city_id = data.get('originCityId')

    # Basic validation
    if budget is None or not match_ids or not origin_city_id:
        return jsonify({"error": "Missing required fields"}), 400

    # 2. Fetch matches by IDs from the database
    matches = Match.query.filter(Match.id.in_(match_ids)).all()

    if not matches:
        return jsonify({"error": "No matches found for given IDs"}), 404
    
    if len(matches) != len(match_ids):
        return jsonify({"error": "Some match IDs were not found"}), 400

    # 3. Convert matches to dicts (using match.to_dict())
    match_dicts = [match.to_dict() for match in matches]

    # 4. Fetch all flight prices from the database
    flight_prices = FlightPrice.query.all()
    flight_price_dicts = [fp.to_dict() for fp in flight_prices]

    # 5. Create a CostCalculator instance
    from app.services.cost_calculator import CostCalculator
    calculator = CostCalculator()

    # 6. Call calculator.calculate(match_dicts, budget, origin_city_id, flight_prices)
    result = calculator.calculate(
        match_dicts,
        budget,
        origin_city_id,
        flight_price_dicts
    )

    # 7. Return the BudgetResult as JSON
    return jsonify(result), 200


# ============================================================
#  POST /api/route/best-value — Find best match combination within budget
# ============================================================
#
# TODO: Implement this endpoint (BONUS CHALLENGE #1)
#
# Request body:
# {
#   "budget": 5000.00,
#   "originCityId": "city-atlanta"
# }
#
# Steps:
#   1. Extract budget and originCityId from request JSON
#   2. Fetch all available matches from the database
#   3. Convert matches to dicts (using match.to_dict())
#   4. Fetch all flight prices from the database
#   5. Create a BestValueFinder instance
#   6. Call finder.find_best_value(match_dicts, budget, origin_city_id, flight_prices)
#   7. Return the BestValueResult as JSON
#
# Requirements:
#   - Find the maximum number of matches that fit within budget
#   - Must include at least 1 match in each country (USA, Mexico, Canada)
#   - Minimum 5 matches required
#   - Return optimised route with cost breakdown
#
# ============================================================

@optimise_bp.route('/best-value', methods=['POST'])
def best_value():
    # TODO: Replace with your implementation (BONUS CHALLENGE #1)

    # 1. Extract budget and originCityId from request JSON
    data = request.get_json()

    budget = data.get('budget')
    origin_city_id = data.get('originCityId')

    # Basic validation
    if budget is None or not origin_city_id:
        return jsonify({"error": "budget and originCityId are required"}), 400

    # 2. Fetch all available matches from the database
    matches = Match.query.all()

    if not matches:
        return jsonify({"error": "No matches available"}), 404

    # 3. Convert matches to dicts (using match.to_dict())
    match_dicts = [match.to_dict() for match in matches]

    # 4. Fetch all flight prices from the database
    flight_prices = FlightPrice.query.all()
    flight_price_dicts = [fp.to_dict() for fp in flight_prices]

    # 5. Create a BestValueFinder instance
    from app.services.best_value_finder import BestValueFinder
    finder = BestValueFinder()

    # 6. Call finder.find_best_value(match_dicts, budget, origin_city_id, flight_prices)
    result = finder.find_best_value(
        match_dicts,
        budget,
        origin_city_id,
        flight_price_dicts
    )

    # 7. Return the BestValueResult as JSON
    return jsonify(result), 200