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

from fhir_mcp_server.compactor.types import Ratio


def compact_ratio(payload):
    return Ratio.model_validate(payload).compact()


class TestCompactRatio:
    """Test direct compact behavior for Ratio payloads."""

    def test_numerator_and_denominator(self):
        """Test that numerator and denominator are joined with a slash."""
        v = {
            "numerator": {"value": 1, "unit": "mg"},
            "denominator": {"value": 10, "unit": "mL"},
        }
        assert compact_ratio(v) == "1 mg/10 mL"

    def test_missing_denominator_returns_empty_string(self):
        """Test that a missing denominator has no compacted output."""
        v = {"numerator": {"value": 1, "unit": "mg"}}
        assert compact_ratio(v) == ""

    def test_missing_numerator_returns_empty_string(self):
        """Test that a missing numerator has no compacted output."""
        v = {"denominator": {"value": 10, "unit": "mL"}}
        assert compact_ratio(v) == ""
