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

from fhir_mcp_server.compactor.types import Address


def compact_address(payload):
    return Address.model_validate(payload).compact()


class TestCompactAddress:
    """Test direct compact behavior for Address payloads."""

    def test_full_address(self):
        """Test that all address fields are compacted correctly."""
        v = {
            "line": ["123 Main St"],
            "city": "Boston",
            "state": "MA",
            "postalCode": "02101",
            "country": "US",
        }
        assert compact_address(v) == "123 Main St, Boston MA 02101, US"

    def test_uses_text_when_present(self):
        """Test that the text field takes precedence over structured address parts."""
        # text + city ensures HumanName validation fails (no city field) and Address is reached
        v = {"text": "123 Main St, Boston MA 02101", "city": "Boston"}
        assert compact_address(v) == "123 Main St, Boston MA 02101"

    def test_district_included_in_location(self):
        """Test that district is included between city and state."""
        v = {
            "city": "Boston",
            "district": "Suffolk",
            "state": "MA",
            "postalCode": "02101",
        }
        assert compact_address(v) == "Boston Suffolk MA 02101"

    def test_use_and_type_appended(self):
        """Test that use and type are appended in parentheses."""
        v = {"use": "home", "type": "postal", "line": ["123 Main St"], "city": "Boston"}
        assert compact_address(v) == "123 Main St, Boston (home, postal)"

    def test_use_only(self):
        """Test that use alone is appended in parentheses when type is absent."""
        v = {"use": "work", "city": "Boston"}
        assert compact_address(v) == "Boston (work)"
