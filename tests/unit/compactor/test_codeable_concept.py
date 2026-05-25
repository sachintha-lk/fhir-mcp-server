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

from fhir_mcp_server.compactor.types import CodeableConcept


def compact_codeable_concept(payload):
    return CodeableConcept.model_validate(payload).compact()


class TestCompactCodeableConcept:
    """Test direct compact behavior for CodeableConcept payloads."""

    def test_uses_text_when_present(self):
        """Test that text field takes precedence over coding."""
        v = {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "8302-2",
                    "display": "Body Height",
                }
            ],
            "text": "Body Height",
        }
        assert compact_codeable_concept(v) == "Body Height"

    def test_text_only_no_coding(self):
        """Test that text-only CodeableConcept compacts to the text value."""
        assert (
            compact_codeable_concept({"text": "uncoded free text result"})
            == "uncoded free text result"
        )

    def test_uses_display_and_code_when_no_text(self):
        """Test that display and code are combined when text is absent."""
        v = {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "8302-2",
                    "display": "Body Height",
                }
            ]
        }
        assert compact_codeable_concept(v) == "Body Height (8302-2)"

    def test_display_only_no_code(self):
        """Test that display alone is used when code is absent."""
        v = {"coding": [{"display": "Body Height"}]}
        assert compact_codeable_concept(v) == "Body Height"

    def test_uses_system_and_code_when_no_display(self):
        """Test that system and code are combined when display is absent."""
        v = {"coding": [{"system": "http://loinc.org", "code": "8302-2"}]}
        assert compact_codeable_concept(v) == "http://loinc.org|8302-2"

    def test_code_only_no_system_no_display(self):
        """Test that bare code is returned when system and display are absent."""
        v = {"coding": [{"code": "8302-2"}]}
        assert compact_codeable_concept(v) == "8302-2"

    def test_empty_coding_returns_empty_string(self):
        """Test that unresolvable coding has no compacted output."""
        v = {"coding": [{"userSelected": True}]}
        assert compact_codeable_concept(v) == ""

    def test_multiple_codings_uses_first(self):
        """Test that only the first coding entry is used."""
        v = {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "8302-2",
                    "display": "Body Height",
                },
                {"system": "https://acme.lab/codes", "code": "HT", "display": "Height"},
            ]
        }
        assert compact_codeable_concept(v) == "Body Height (8302-2)"
