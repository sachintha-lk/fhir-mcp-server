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

from fhir_mcp_server.compactor.types import Range


def compact_range(payload):
    return Range.model_validate(payload).compact()


class TestCompactRange:
    """Test direct compact behavior for Range payloads."""

    def test_low_and_high(self):
        """Test that low and high bounds are joined with an en-dash."""
        v = {
            "low": {"value": 3.5, "unit": "mmol/L"},
            "high": {"value": 5.5, "unit": "mmol/L"},
        }
        assert compact_range(v) == "3.5 mmol/L – 5.5 mmol/L"

    def test_only_low(self):
        """Test that only the low bound is returned when high is absent."""
        v = {"low": {"value": 3.5, "unit": "mmol/L"}}
        assert compact_range(v) == "3.5 mmol/L"

    def test_only_high(self):
        """Test that only the high bound is returned when low is absent."""
        v = {"high": {"value": 5.5, "unit": "mmol/L"}}
        assert compact_range(v) == "5.5 mmol/L"

    def test_equal_bounds_compact(self):
        """Test that equal low and high bounds compact to an en-dash range."""
        assert compact_range({"low": {"value": 5.0}, "high": {"value": 5.0}}) == "5 – 5"
