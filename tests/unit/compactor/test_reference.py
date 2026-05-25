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

from fhir_mcp_server.compactor.types import Reference


def compact_reference(payload):
    return Reference.model_validate(payload).compact()


class TestCompactReference:
    """Test direct compact behavior for Reference payloads."""

    def test_display_and_reference(self):
        """Test that display and reference are combined when both are present."""
        v = {"reference": "Patient/123", "display": "Amy Shaw"}
        assert compact_reference(v) == "Amy Shaw [Patient/123]"

    def test_display_only(self):
        """Test that display alone is returned when reference is absent."""
        v = {"display": "GP Visit"}
        assert compact_reference(v) == "GP Visit"

    def test_reference_only(self):
        """Test that reference alone is returned when display is absent."""
        v = {"reference": "Patient/123"}
        assert compact_reference(v) == "Patient/123"

    def test_identifier_with_type(self):
        """Test that identifier and type are combined when reference and display are absent."""
        v = {
            "type": "Patient",
            "identifier": {"system": "http://hospital.org/mrn", "value": "X"},
        }
        assert compact_reference(v) == "Patient: http://hospital.org/mrn|X"
