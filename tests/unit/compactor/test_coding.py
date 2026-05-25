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

from fhir_mcp_server.compactor.types import Coding


def compact_coding(payload):
    return Coding.model_validate(payload).compact()


class TestCompactCoding:
    """Test direct compact behavior for Coding payloads."""

    def test_uses_display_and_code(self):
        """Test that display and code are combined."""
        v = {"system": "http://loinc.org", "code": "8302-2", "display": "Body Height"}
        assert compact_coding(v) == "Body Height (8302-2)"

    def test_display_only(self):
        """Test that display alone is returned when code is absent."""
        v = {"display": "Body Height"}
        assert compact_coding(v) == "Body Height"

    def test_uses_system_and_code_when_no_display(self):
        """Test that system and code are combined when display is absent."""
        v = {"system": "http://loinc.org", "code": "8302-2"}
        assert compact_coding(v) == "http://loinc.org|8302-2"

    def test_code_only(self):
        """Test that bare code is returned when system and display are absent."""
        v = {"code": "8302-2"}
        assert compact_coding(v) == "8302-2"
