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

from fhir_mcp_server.compactor.dispatch import compact_resource
from fhir_mcp_server.compactor.registry import COMPLEX_DATA_TYPES


class TestCompactResourceDispatch:
    """Test compact_resource list handling and recursive dispatch behavior."""

    def test_complex_data_type_order_is_explicit(self):
        """Test the precedence order used to resolve ambiguous FHIR datatype shapes."""
        assert [data_type.__name__ for data_type in COMPLEX_DATA_TYPES] == [
            "Ratio",
            "Range",
            "Money",
            "Annotation",
            "Period",
            "HumanName",
            "Address",
            "Coding",
            "CodeableConcept",
            "Quantity",
            "Extension",
            "Attachment",
            "ContactPoint",
            "Identifier",
            "Reference",
            "Timing",
        ]

    def test_compacts_each_item_in_list(self):
        """Test that each item in a list is individually compacted."""
        data = [
            {"coding": [{"code": "M", "display": "Married"}]},
            {"coding": [{"code": "S", "display": "Single"}]},
        ]
        assert compact_resource(data) == ["Married (M)", "Single (S)"]

    def test_leaves_primitives_unchanged(self):
        """Test that primitive values are returned unchanged."""
        assert compact_resource("hello") == "hello"
        assert compact_resource(42) == 42
        assert compact_resource(True) is True

    def test_recurses_into_unrecognized_dict(self):
        """Test that unrecognized dicts are recursed into and their values compacted."""
        data = {
            "resourceType": "Patient",
            "valueQuantity": {"value": 7.2, "unit": "cm"},
        }
        assert compact_resource(data) == {
            "resourceType": "Patient",
            "valueQuantity": "7.2 cm",
        }

    def test_empty_compact_result_returns_original_payload(self):
        """Test that a matched datatype with no compact output stops dispatch."""
        payload = {"coding": [{"userSelected": True}]}

        assert compact_resource(payload) == payload

    def test_human_name_precedes_address_and_codeable_concept(self):
        """Test dispatch precedence for text/use payloads accepted by multiple types."""
        payload = {"text": "Johnny", "use": "nickname"}

        assert compact_resource(payload) == "Johnny (nickname)"

    def test_contact_point_precedes_identifier_for_value_and_use(self):
        """Test dispatch precedence for value/use payloads accepted by both types."""
        payload = {"value": "MRN123", "use": "official"}

        assert compact_resource(payload) == "MRN123 (official)"

    def test_extension_precedes_attachment_for_url_only_payload(self):
        """Test that Extension's empty result prevents Attachment fallback."""
        payload = {"url": "http://example.com/image.png"}

        assert compact_resource(payload) == payload


class TestRealWorldPayloads:
    """Test compact_resource against official FHIR example payloads."""

    def test_us_core_blood_pressure(self):
        """Test compaction of the US Core Blood Pressure Observation example."""
        # The exact US Core Blood Pressure JSON payload
        payload = {
            "resourceType": "Observation",
            "id": "blood-pressure",
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-blood-pressure|9.0.0"
                ]
            },
            "text": {
                "status": "generated",
                "div": '<div xmlns="http://www.w3.org/1999/xhtml"><p class="res-header-id"><b>Generated Narrative: Observation blood-pressure</b></p><a name="blood-pressure"> </a><a name="hcblood-pressure"> </a><div style="display: inline-block; background-color: #d9e0e7; padding: 6px; margin: 4px; border: 1px solid #8da1b4; border-radius: 5px; line-height: 60%"><p style="margin-bottom: 0px"/><p style="margin-bottom: 0px">Profile: <a href="StructureDefinition-us-core-blood-pressure.html">US Core Blood Pressure Profile</a> version: 9.0.0</p></div><p><b>status</b>: Final</p><p><b>category</b>: <span title="Codes:{http://terminology.hl7.org/CodeSystem/observation-category vital-signs}">Vital Signs</span></p><p><b>code</b>: <span title="Codes:{http://loinc.org 85354-9}">Blood pressure systolic and diastolic</span></p><p><b>subject</b>: <a href="Patient-example.html">Amy Shaw</a></p><p><b>encounter</b>: GP Visit</p><p><b>effective</b>: 1999-07-02</p><p><b>performer</b>: <a href="Practitioner-practitioner-1.html">Dr Ronald Bone</a></p><blockquote><p><b>component</b></p><p><b>code</b>: <span title="Codes:{http://loinc.org 8480-6}">Systolic blood pressure</span></p><p><b>value</b>: 109 mmHg<span style="background: LightGoldenRodYellow"> (Details: UCUM  codemm[Hg] = \'mm[Hg]\')</span></p></blockquote><blockquote><p><b>component</b></p><p><b>code</b>: <span title="Codes:{http://loinc.org 8462-4}">Diastolic blood pressure</span></p><p><b>value</b>: 44 mmHg<span style="background: LightGoldenRodYellow"> (Details: UCUM  codemm[Hg] = \'mm[Hg]\')</span></p></blockquote></div>',
            },
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
                        "display": "Blood pressure panel with all children optional",
                    }
                ],
                "text": "Blood pressure systolic and diastolic",
            },
            "subject": {"reference": "Patient/example", "display": "Amy Shaw"},
            "encounter": {"display": "GP Visit"},
            "effectiveDateTime": "1999-07-02",
            "performer": [
                {
                    "reference": "Practitioner/practitioner-1",
                    "display": "Dr Ronald Bone",
                }
            ],
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
                        "system": "http://unitsofmeasure.org",
                        "code": "mm[Hg]",
                    },
                },
                {
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8462-4",
                                "display": "Diastolic blood pressure",
                            }
                        ],
                        "text": "Diastolic blood pressure",
                    },
                    "valueQuantity": {
                        "value": 44,
                        "unit": "mmHg",
                        "system": "http://unitsofmeasure.org",
                        "code": "mm[Hg]",
                    },
                },
            ],
        }

        result = compact_resource(payload)

        assert result["resourceType"] == "Observation"
        assert result["code"] == "Blood pressure systolic and diastolic"
        assert result["category"] == ["Vital Signs"]

        # Components should be cleanly flattened
        assert len(result["component"]) == 2

        assert result["component"][0]["code"] == "Systolic blood pressure"
        assert result["component"][0]["valueQuantity"] == "109 mmHg"

        assert result["component"][1]["code"] == "Diastolic blood pressure"
        assert result["component"][1]["valueQuantity"] == "44 mmHg"
