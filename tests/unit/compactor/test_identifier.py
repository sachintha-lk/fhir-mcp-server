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

from fhir_mcp_server.compactor.types import Identifier


def compact_identifier(payload):
    return Identifier.model_validate(payload).compact()


class TestCompactIdentifier:
    """Test direct compact behavior for Identifier payloads."""

    def test_system_value_and_use(self):
        """Test that system, value, and use are compacted correctly."""
        v = {"system": "http://hospital.org/mrn", "value": "MRN123", "use": "official"}
        assert compact_identifier(v) == "http://hospital.org/mrn|MRN123 [official]"

    def test_system_and_value(self):
        """Test that system and value are joined when use is absent."""
        v = {"system": "http://hospital.org/mrn", "value": "MRN123"}
        assert compact_identifier(v) == "http://hospital.org/mrn|MRN123"

    def test_type_prepended_as_label(self):
        """Test that the type text is prepended as a label."""
        v = {
            "type": {"text": "MRN"},
            "system": "http://hospital.org/mrn",
            "value": "MRN123",
        }
        assert compact_identifier(v) == "MRN: http://hospital.org/mrn|MRN123"

    def test_value_only(self):
        """Test that value alone is returned when system is absent."""
        assert compact_identifier({"value": "MRN123"}) == "MRN123"

    def test_system_only(self):
        """Test that system alone is returned when value is absent."""
        assert (
            compact_identifier({"system": "http://hospital.org/mrn"})
            == "http://hospital.org/mrn"
        )
