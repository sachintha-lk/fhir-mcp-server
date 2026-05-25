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

from fhir_mcp_server.compactor.types import HumanName


def compact_human_name(payload):
    return HumanName.model_validate(payload).compact()


class TestCompactHumanName:
    """Test direct compact behavior for HumanName payloads."""

    def test_full_name_with_prefix(self):
        """Test that prefix, given, and family are joined in order."""
        v = {"use": "official", "family": "Smith", "given": ["John"], "prefix": ["Dr."]}
        assert compact_human_name(v) == "Dr. John Smith"

    def test_nickname_appends_use(self):
        """Test that non-official use values are appended in parentheses."""
        v = {"use": "nickname", "given": ["Johnny"]}
        assert compact_human_name(v) == "Johnny (nickname)"

    def test_uses_text_when_present(self):
        """Test that the text field takes precedence over structured name parts."""
        v = {"text": "John Smith", "family": "Smith", "given": ["John"]}
        assert compact_human_name(v) == "John Smith"

    def test_text_with_non_official_use_appends_use(self):
        """Test that text values retain non-official use values."""
        v = {"text": "Johnny", "use": "nickname"}
        assert compact_human_name(v) == "Johnny (nickname)"

    def test_text_with_official_use_suppresses_use(self):
        """Test that official use is not appended to text values."""
        v = {"text": "John Smith", "use": "official"}
        assert compact_human_name(v) == "John Smith"

    def test_suffix_appended(self):
        """Test that suffix is appended after the family name."""
        v = {"family": "Smith", "given": ["John"], "suffix": ["Jr."]}
        assert compact_human_name(v) == "John Smith Jr."

    def test_official_use_suppressed(self):
        """Test that 'official' use is not appended to the name."""
        v = {"use": "official", "family": "Smith", "given": ["John"]}
        assert compact_human_name(v) == "John Smith"

    def test_maiden_use_shown(self):
        """Test that 'maiden' use is appended in parentheses."""
        v = {"use": "maiden", "family": "Jones", "given": ["Jane"]}
        assert compact_human_name(v) == "Jane Jones (maiden)"

    def test_usual_use_shown(self):
        """Test that 'usual' use is appended in parentheses."""
        v = {"use": "usual", "family": "Smith", "given": ["Johnny"]}
        assert compact_human_name(v) == "Johnny Smith (usual)"
