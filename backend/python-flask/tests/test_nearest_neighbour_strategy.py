import pytest
from app.strategies.nearest_neighbour_strategy import NearestNeighbourStrategy


class TestNearestNeighbourStrategy:

    def setup_method(self):
        self.strategy = NearestNeighbourStrategy()

    def _create_match(self, match_id, kickoff, city_id, lat, lon):
        return {
            "id": match_id,
            "kickoff": kickoff,
            "city": {
                "id": city_id,
                "name": city_id,
                "latitude": lat,
                "longitude": lon
            }
        }

    def test_happy_path_returns_valid_route(self):
        """Should return a valid route for multiple matches (happy path)"""
        # Arrange: Create an array of matches across different cities and dates
        matches = [
            self._create_match("m1", "2026-06-10T10:00:00", "city-a", 0, 0),
            self._create_match("m2", "2026-06-11T10:00:00", "city-b", 10, 10),
            self._create_match("m3", "2026-06-12T10:00:00", "city-c", 20, 20),
        ]

        # Act: Call self.strategy.optimise(matches)
        result = self.strategy.optimise(matches)

        # Assert: Verify the result has stops, totalDistance > 0, and strategy = 'nearest-neighbour'
        assert result is not None
        assert "stops" in result
        assert len(result["stops"]) == 3
        assert result["totalDistance"] > 0
        assert result["strategy"] == "nearest-neighbour"

    def test_empty_matches_returns_empty_route(self):
        """Should return an empty route for empty matches"""
        # Arrange: Create an empty array of matches
        matches = []

        # Act: Call self.strategy.optimise([])
        result = self.strategy.optimise(matches)

        # Assert: Verify the result has empty stops and totalDistance = 0
        assert result is not None
        assert "stops" in result
        assert len(result["stops"]) == 0
        assert result["totalDistance"] == 0

    def test_single_match_returns_zero_distance(self):
        """Should return zero distance for a single match"""
        # Arrange: Create an array with a single match
        matches = [
            self._create_match("m1", "2026-06-10T10:00:00", "city-a", 0, 0)
        ]

        # Act: Call self.strategy.optimise(matches)
        result = self.strategy.optimise(matches)

        # Assert: Verify totalDistance = 0 and len(stops) = 1
        assert result is not None
        assert len(result["stops"]) == 1
        assert result["totalDistance"] == 0