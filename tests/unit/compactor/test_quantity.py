# Copyright (c) 2026, WSO2 LLC. (https://www.wso2.com/) All Rights Reserved.

# WSO2 LLC. licenses this file to you under the Apache License,
# Version 2.0 (the "License"); you may not use this file except
# in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.

from fhir_mcp_server.compactor.types import Quantity


def compact_quantity(payload):
    return Quantity.model_validate(payload).compact()


class TestCompactQuantity:
    """Test direct compact behavior for Quantity payloads."""

    def test_value_and_unit(self):
        """Test that value and unit are joined with a space."""
        assert compact_quantity({"value": 7.2, "unit": "mmol/L"}) == "7.2 mmol/L"

    def test_with_comparator(self):
        """Test that comparator is prepended to the value."""
        assert (
            compact_quantity({"value": 5.0, "comparator": ">=", "unit": "mg/dL"})
            == ">=5 mg/dL"
        )

    def test_integer_value_no_trailing_zeros(self):
        """Test that integer values are rendered without decimal places."""
        assert compact_quantity({"value": 150, "unit": "cm"}) == "150 cm"

    def test_value_only_no_unit(self):
        """Test that value alone is returned when unit is absent."""
        assert (
            compact_quantity({"value": 42, "system": "http://unitsofmeasure.org"})
            == "42"
        )

    def test_unit_only_no_value(self):
        """Test that unit alone is returned when value is absent."""
        assert compact_quantity({"unit": "cm"}) == "cm"


class TestCompactQuantityAliases:
    """Test Quantity-shaped payloads used by constrained FHIR quantity aliases."""

    def test_age(self):
        """Test Age subtype compaction."""
        assert compact_quantity({"value": 30, "unit": "yr"}) == "30 yr"

    def test_count(self):
        """Test Count subtype compaction."""
        assert compact_quantity({"value": 3, "unit": "{count}"}) == "3 {count}"

    def test_distance(self):
        """Test Distance subtype compaction."""
        assert compact_quantity({"value": 5, "unit": "km"}) == "5 km"

    def test_duration(self):
        """Test Duration subtype compaction."""
        assert compact_quantity({"value": 30, "unit": "min"}) == "30 min"

    def test_money_quantity(self):
        """Test MoneyQuantity subtype compaction."""
        assert (
            compact_quantity(
                {"value": 100, "unit": "USD", "system": "urn:iso:std:iso:4217"}
            )
            == "100 USD"
        )

    def test_simple_quantity(self):
        """Test SimpleQuantity subtype compaction."""
        assert compact_quantity({"value": 5, "unit": "mg"}) == "5 mg"
