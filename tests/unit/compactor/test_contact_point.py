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

from fhir_mcp_server.compactor.types import ContactPoint


def compact_contact_point(payload):
    return ContactPoint.model_validate(payload).compact()


class TestCompactContactPoint:
    """Test direct compact behavior for ContactPoint payloads."""

    def test_phone_with_use(self):
        """Test that system, value, and use are compacted correctly."""
        assert (
            compact_contact_point(
                {"system": "phone", "value": "555-1234", "use": "home"}
            )
            == "phone: 555-1234 (home)"
        )

    def test_email_without_use(self):
        """Test that system and value are compacted without use when absent."""
        assert (
            compact_contact_point({"system": "email", "value": "john@example.com"})
            == "email: john@example.com"
        )

    def test_rank_appended(self):
        """Test that rank is appended with a # prefix."""
        v = {"system": "phone", "value": "555-1234", "use": "home", "rank": 1}
        assert compact_contact_point(v) == "phone: 555-1234 (home) #1"
