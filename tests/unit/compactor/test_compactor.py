# Copyright (c) 2026, WSO2 LLC. (https://www.wso2.com/) All Rights Reserved.
#
# WSO2 LLC. licenses this file to you under the Apache License,
# Version 2.0 (the "License"); you may not use this file except
# in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Routing and tree traversal tests for compact_datatypes.

Unlike individual type tests (e.g., test_money.py) which verify isolated type compaction,
these tests validate that the central COMPACTOR_ADAPTER correctly walks complex
payloads and routes anonymous dictionaries to the right FHIR model (discriminator routing).
"""

import pytest
from fhir_mcp_server.compactor import compact_datatypes


class TestTraversal:
    """Test compact_datatypes list handling and recursive tree traversal behavior."""

    def test_compacts_each_item_in_list(self):
        """Test that each item in a list is individually compacted recursively."""
        data = [
            {"coding": [{"code": "M", "display": "Married"}]},
            {"coding": [{"code": "S", "display": "Single"}]},
        ]
        assert compact_datatypes(data) == ["Married (M)", "Single (S)"]

    def test_leaves_primitives_unchanged(self):
        """Test that primitive values are returned unchanged."""
        assert compact_datatypes("hello") == "hello"
        assert compact_datatypes(42) == 42
        assert compact_datatypes(True) is True

    def test_recurses_into_unrecognized_dict(self):
        """Test that unrecognized dicts are recursed into and their values compacted."""
        data = {
            "resourceType": "Patient",
            "valueQuantity": {"value": 7.2, "unit": "cm"},
        }
        assert compact_datatypes(data) == {
            "resourceType": "Patient",
            "valueQuantity": "7.2 cm",
        }

    def test_empty_compact_result_returns_original_payload(self):
        """Test that a matched datatype with no compact output stops dispatch and returns original payload."""
        payload = {"coding": [{"userSelected": True}]}
        assert compact_datatypes(payload) == payload

    def test_discriminator_with_non_dict(self):
        """Verify discriminator returns pass_through when input is not a dict to guarantee full statement coverage."""
        from fhir_mcp_server.compactor.discriminator import fhir_type_discriminator
        assert fhir_type_discriminator("not a dict") == "pass_through"
        assert fhir_type_discriminator(None) == "pass_through"


class TestStandard:
    """Verify that generic payloads route correctly to their corresponding FHIR models."""

    def test_money_routing(self):
        """Verify anonymous payload routes to Money model and compacts correctly."""
        assert compact_datatypes({"value": 49.99, "currency": "USD"}) == "49.99 USD"

    def test_period_routing(self):
        """Verify anonymous payload routes to Period model across all routing key branches."""
        assert compact_datatypes({"start": "2026-01-01", "end": "2026-12-31"}) == "2026-01-01 – 2026-12-31"
        assert compact_datatypes({"start": "2026-01-01"}) == "from 2026-01-01"
        assert compact_datatypes({"end": "2026-12-31"}) == "until 2026-12-31"

    def test_quantity_routing(self):
        """Verify anonymous payload routes to Quantity model across all routing key branches."""
        assert compact_datatypes({"value": 7.2, "unit": "mmol/L"}) == "7.2 mmol/L"
        assert compact_datatypes({"value": 5.0, "comparator": ">=", "unit": "mg/dL"}) == ">=5 mg/dL"

    def test_range_routing(self):
        """Verify anonymous payload routes to Range model and compacts correctly."""
        payload = {
            "low": {"value": 10, "unit": "mg"},
            "high": {"value": 20, "unit": "mg"},
        }
        assert compact_datatypes(payload) == "10 mg – 20 mg"

    def test_ratio_routing(self):
        """Verify anonymous payload routes to Ratio model and compacts correctly."""
        payload = {
            "numerator": {"value": 5, "unit": "mg"},
            "denominator": {"value": 10, "unit": "mL"},
        }
        assert compact_datatypes(payload) == "5 mg/10 mL"

    def test_coding_routing(self):
        """Verify anonymous payload routes to Coding model and compacts correctly."""
        assert compact_datatypes({"code": "M", "display": "Married"}) == "Married (M)"

    def test_codeable_concept_routing(self):
        """Verify anonymous payload routes to CodeableConcept model across all routing key branches."""
        payload_with_text = {
            "coding": [{"code": "34068001", "display": "Heart failure"}],
            "text": "Cardiovascular issues",
        }
        assert compact_datatypes(payload_with_text) == "Cardiovascular issues"

        payload_no_text = {
            "coding": [{"code": "34068001", "display": "Heart failure"}]
        }
        assert compact_datatypes(payload_no_text) == "Heart failure (34068001)"

    def test_human_name_routing(self):
        """Verify anonymous payload routes to HumanName model and compacts correctly."""
        payload = {
            "given": ["John"],
            "family": "Smith",
            "prefix": ["Dr."],
            "suffix": ["PhD"],
            "use": "official",
        }
        assert compact_datatypes(payload) == "Dr. John Smith PhD"

    def test_address_routing(self):
        """Verify anonymous payload routes to Address model and compacts correctly."""
        payload = {
            "line": ["123 Main St"],
            "city": "Boston",
            "state": "MA",
            "postalCode": "02110",
            "country": "USA",
            "use": "work",
        }
        assert compact_datatypes(payload) == "123 Main St, Boston MA 02110, USA (work)"

    def test_contact_point_routing(self):
        """Verify anonymous payload routes to ContactPoint model and compacts correctly."""
        payload = {"system": "phone", "value": "555-0199", "use": "home"}
        assert compact_datatypes(payload) == "phone: 555-0199 (home)"

    def test_identifier_routing(self):
        """Verify anonymous payload routes to Identifier model and compacts correctly."""
        payload = {
            "system": "http://hl7.org/fhir/sid/us-ssn",
            "value": "000-12-3456",
            "use": "official",
        }
        assert compact_datatypes(payload) == "http://hl7.org/fhir/sid/us-ssn|000-12-3456 [official]"

    def test_reference_routing(self):
        """Verify anonymous payload routes to Reference model across all routing key branches."""
        assert compact_datatypes({"reference": "Patient/example", "display": "Amy Shaw"}) == "Amy Shaw [Patient/example]"
        assert compact_datatypes({"display": "GP Visit"}) == "GP Visit"

    def test_annotation_routing(self):
        """Verify anonymous payload routes to Annotation model and compacts correctly."""
        payload = {
            "authorString": "Dr. Bone",
            "time": "2026-05-27T10:00:00Z",
            "text": "Patient is recovering well.",
        }
        assert compact_datatypes(payload) == "Patient is recovering well. (Dr. Bone, 2026-05-27T10:00:00Z)"

    def test_attachment_routing(self):
        """Verify anonymous payload routes to Attachment model and compacts correctly."""
        payload = {
            "contentType": "image/png",
            "url": "http://example.com/photo.png",
            "title": "Patient Photo",
        }
        assert compact_datatypes(payload) == "Patient Photo (image/png)"

    def test_timing_routing(self):
        """Verify anonymous payload routes to Timing model."""
        assert compact_datatypes({"repeat": {"count": 1}}) == "1 time"

    def test_extension_routing(self):
        """Verify anonymous payload routes to Extension model across all key branches."""
        assert compact_datatypes({"url": "http://example.org/ext", "valueDecimal": 3.14}) == "http://example.org/ext|3.14"
        payload_nested = {
            "url": "http://example.org/race",
            "extension": [{"url": "text", "valueString": "Mixed"}]
        }
        assert compact_datatypes(payload_nested) == {
            "url": "http://example.org/race",
            "text": "Mixed"
        }
        assert compact_datatypes({"url": "http://example.org/url-only"}) == {"url": "http://example.org/url-only"}


class TestAmbiguous:
    """Verify that overlapping/ambiguous payloads route safely without misclassifications."""

    def test_bare_value_resolves_to_quantity_not_money(self):
        """Verify single 'value' field matches Quantity rather than Money."""
        assert compact_datatypes({"value": 120}) == "120"

    def test_overlapping_value_use_resolves_to_contact_point(self):
        """Verify 'value' + 'use' overlaps prioritize ContactPoint over Identifier."""
        assert compact_datatypes({"value": "MRN123", "use": "official"}) == "MRN123 (official)"

    def test_overlapping_text_use_resolves_to_human_name(self):
        """Verify 'text' + 'use' overlaps prioritize HumanName in dispatch order."""
        assert compact_datatypes({"text": "Johnny", "use": "nickname"}) == "Johnny (nickname)"

    def test_unknown_dictionary_passes_through_recursively(self):
        """Verify unrecognized fields do not match any model and walk recursively."""
        payload = {"randomField": "randomValue"}
        assert compact_datatypes(payload) == payload


def test_compactor_routing_deep_nested_traversal():
    """Verify recursive traversal handles nested structures containing mixtures of lists, dicts, and primitives."""
    nested_payload = {
        "resourceType": "Observation",
        "id": "obs-example",
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "vital-signs",
                        "display": "Vital Signs",
                    }
                ],
                "text": "Vital Signs",
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "85354-9",
                    "display": "Blood pressure panel",
                }
            ],
            "text": "Blood pressure systolic and diastolic",
        },
        "subject": {"reference": "Patient/example", "display": "Amy Shaw"},
        "effectiveDateTime": "2026-05-27",
        "valueRange": {
            "low": {"value": 60, "unit": "mmHg"},
            "high": {"value": 120, "unit": "mmHg"},
        },
        "component": [
            {
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "8480-6",
                            "display": "Systolic blood pressure",
                        }
                    ],
                    "text": "Systolic blood pressure",
                },
                "valueQuantity": {
                    "value": 109,
                    "unit": "mmHg",
                },
            }
        ],
        "notes": [
            {
                "authorString": "Nurse Joy",
                "text": "Resting comfortably.",
            }
        ],
    }

    expected_compacted = {
        "resourceType": "Observation",
        "id": "obs-example",
        "status": "final",
        "category": ["Vital Signs"],
        "code": "Blood pressure systolic and diastolic",
        "subject": "Amy Shaw [Patient/example]",
        "effectiveDateTime": "2026-05-27",
        "valueRange": "60 mmHg – 120 mmHg",
        "component": [
            {
                "code": "Systolic blood pressure",
                "valueQuantity": "109 mmHg",
            }
        ],
        "notes": ["Resting comfortably. (Nurse Joy)"],
    }

    assert compact_datatypes(nested_payload) == expected_compacted
