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

from fhir_mcp_server.compactor.types import Annotation


def compact_annotation(payload):
    return Annotation.model_validate(payload).compact()


class TestCompactAnnotation:
    """Test direct compact behavior for Annotation payloads."""

    def test_text_only(self):
        """Test that text alone is returned as-is."""
        v = {"text": "Patient was fasting"}
        assert compact_annotation(v) == "Patient was fasting"

    def test_text_with_time(self):
        """Test that time is appended in parentheses."""
        v = {"text": "Patient was fasting", "time": "2024-01-01T09:00:00Z"}
        assert compact_annotation(v) == "Patient was fasting (2024-01-01T09:00:00Z)"

    def test_text_with_author_string(self):
        """Test that authorString is appended in parentheses."""
        v = {"text": "Patient was fasting", "authorString": "Dr. Smith"}
        assert compact_annotation(v) == "Patient was fasting (Dr. Smith)"

    def test_text_with_author_and_time(self):
        """Test that author and time are both appended, comma-separated."""
        v = {
            "text": "Patient was fasting",
            "authorString": "Dr. Smith",
            "time": "2024-01-01",
        }
        assert compact_annotation(v) == "Patient was fasting (Dr. Smith, 2024-01-01)"

    def test_author_reference(self):
        """Test that authorReference is resolved to its reference string."""
        v = {
            "text": "I don't think this is true",
            "authorReference": {"reference": "Patient/example"},
            "time": "2022-02-08T10:18:14Z",
        }
        assert (
            compact_annotation(v)
            == "I don't think this is true (Patient/example, 2022-02-08T10:18:14Z)"
        )
