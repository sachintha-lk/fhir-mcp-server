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

from fhir_mcp_server.compactor.types import Extension


def compact_extension(payload):
    return Extension.model_validate(payload).compact()


class TestCompactExtension:
    """Test direct compact behavior for Extension payloads (flat and nested)."""

    # us-core-interpreter-needed — flat valueCoding extension
    INTERPRETER_NEEDED = {
        "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-interpreter-needed",
        "valueCoding": {
            "system": "http://snomed.info/sct",
            "version": "http://snomed.info/sct/731000124108",
            "code": "373066001",
        },
    }

    # us-core-race — nested extension with repeated ombCategory sub-URLs
    RACE = {
        "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race",
        "extension": [
            {
                "url": "ombCategory",
                "valueCoding": {
                    "system": "urn:oid:2.16.840.1.113883.6.238",
                    "code": "2106-3",
                    "display": "White",
                },
            },
            {
                "url": "ombCategory",
                "valueCoding": {
                    "system": "urn:oid:2.16.840.1.113883.6.238",
                    "code": "1002-5",
                    "display": "American Indian or Alaska Native",
                },
            },
            {
                "url": "ombCategory",
                "valueCoding": {
                    "system": "urn:oid:2.16.840.1.113883.6.238",
                    "code": "2028-9",
                    "display": "Asian",
                },
            },
            {
                "url": "detailed",
                "valueCoding": {
                    "system": "urn:oid:2.16.840.1.113883.6.238",
                    "code": "1586-7",
                    "display": "Shoshone",
                },
            },
            {
                "url": "detailed",
                "valueCoding": {
                    "system": "urn:oid:2.16.840.1.113883.6.238",
                    "code": "2036-2",
                    "display": "Filipino",
                },
            },
            {"url": "text", "valueString": "Mixed"},
        ],
    }

    # us-core-tribal-affiliation — nested with valueCodeableConcept and valueBoolean
    TRIBAL_AFFILIATION = {
        "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-tribal-affiliation",
        "extension": [
            {
                "url": "tribalAffiliation",
                "valueCodeableConcept": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-TribalEntityUS",
                            "code": "187",
                            "display": "Paiute-Shoshone Tribe of the Fallon Reservation and Colony, Nevada",
                        }
                    ],
                    "text": "Shoshone",
                },
            },
            {"url": "isEnrolled", "valueBoolean": False},
        ],
    }

    def test_flat_extension_returns_url_pipe_value(self):
        """Test that a flat extension compacts to url|value."""
        result = compact_extension(self.INTERPRETER_NEEDED)
        assert (
            result
            == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-interpreter-needed|http://snomed.info/sct|373066001"
        )

    def test_nested_extension_returns_dict_keyed_by_sub_url(self):
        """Test that nested extension compacts to a dict keyed by sub-extension URLs."""
        result = compact_extension(self.RACE)
        assert isinstance(result, dict)
        assert (
            result["url"]
            == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race"
        )
        assert result["text"] == "Mixed"

    def test_repeated_sub_url_becomes_list(self):
        """Test that repeated sub-extension URLs are collected into a list."""
        result = compact_extension(self.RACE)
        assert isinstance(result["ombCategory"], list)
        assert result["ombCategory"] == [
            "White (2106-3)",
            "American Indian or Alaska Native (1002-5)",
            "Asian (2028-9)",
        ]
        assert isinstance(result["detailed"], list)
        assert result["detailed"] == ["Shoshone (1586-7)", "Filipino (2036-2)"]

    def test_nested_extension_with_codeable_concept_and_boolean(self):
        """Test that valueCodeableConcept and valueBoolean are compacted in nested extensions."""
        result = compact_extension(self.TRIBAL_AFFILIATION)
        assert isinstance(result, dict)
        assert (
            result["url"]
            == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-tribal-affiliation"
        )
        assert result["tribalAffiliation"] == "Shoshone"
        assert result["isEnrolled"] == "False"

    def test_unresolvable_nested_extension_returns_empty_string(self):
        """Test that a nested extension with no sub-extension values has no compacted output."""
        data = {"url": "http://example.org/ext", "extension": []}
        assert compact_extension(data) == ""

    def test_sub_extension_value_that_compacts_to_dict_is_dropped(self):
        """Test that sub-extensions whose value cannot be reduced to a string are skipped."""
        # valueX that direct compact cannot reduce to a string (unrecognized dict)
        # _extract_extension_value returns "" → sub-extension is skipped
        data = {
            "url": "http://example.org/ext",
            "extension": [
                {"url": "known", "valueString": "hello"},
                {"url": "unknown", "valueX": {"foo": "bar", "baz": 1}},
            ],
        }
        result = compact_extension(data)
        assert isinstance(result, dict)
        assert result["known"] == "hello"
        assert "unknown" not in result

    def test_float_value_in_extension(self):
        """Test that float values are compacted to url|value."""
        data = {"url": "http://example.org/ext", "valueDecimal": 3.14}
        assert compact_extension(data) == "http://example.org/ext|3.14"

    def test_int_value_in_extension(self):
        """Test that integer values are compacted to url|value."""
        data = {"url": "http://example.org/ext", "valueInteger": 42}
        assert compact_extension(data) == "http://example.org/ext|42"

    def test_no_value_keys_returns_empty_string(self):
        """Test that an extension with no value key has no compacted output."""
        data = {"url": "http://example.org/ext"}
        assert compact_extension(data) == ""

    def test_multiple_value_keys_returns_empty_string(self):
        """Test that an extension with multiple value keys has no compacted output."""
        data = {"url": "http://example.org/ext", "valueString": "a", "valueInteger": 1}
        assert compact_extension(data) == ""

    def test_list_value_field_returns_empty_string(self):
        """Test that a list-typed value field cannot be reduced to compacted output."""
        data = {"url": "x", "valueList": [1, 2]}
        assert compact_extension(data) == ""
