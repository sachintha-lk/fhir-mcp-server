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

import pytest
from pydantic import ValidationError
from fhir_mcp_server.compactor.types import Attachment


def compact_attachment(payload):
    return Attachment.model_validate(payload).compact()


class TestCompactAttachment:
    """Test direct compact behavior for Attachment payloads."""

    def test_title_and_content_type(self):
        """Test that title and contentType are combined."""
        v = {"title": "Discharge Summary", "contentType": "application/pdf"}
        assert compact_attachment(v) == "Discharge Summary (application/pdf)"

    def test_title_without_content_type(self):
        """Test that title alone is returned when contentType is absent."""
        v = {"title": "Discharge Summary"}
        assert compact_attachment(v) == "Discharge Summary"

    def test_falls_back_to_url(self):
        """Test that URL is used when title is absent."""
        v = {"url": "http://example.com/image.png", "contentType": "image/png"}
        assert compact_attachment(v) == "http://example.com/image.png"

    def test_content_type_only(self):
        """Test that contentType alone is returned when title and URL are absent."""
        v = {"contentType": "application/pdf"}
        assert compact_attachment(v) == "application/pdf"

    def test_inline_text_data_decoded(self):
        """Test that base64-encoded text data is decoded and returned as a string."""
        import base64

        v = {
            "contentType": "text/plain",
            "data": base64.b64encode(b"hello world").decode(),
        }
        assert compact_attachment(v) == "hello world"

    def test_inline_binary_data_as_data_uri(self):
        """Test that base64-encoded binary data is returned as a data URI."""
        import base64

        raw = b"\x89PNG\r\n"
        v = {"contentType": "image/png", "data": base64.b64encode(raw).decode()}
        assert (
            compact_attachment(v)
            == f"data:image/png;base64,{base64.b64encode(raw).decode()}"
        )

    def test_raw_bytes_data_compacts_to_data_uri(self):
        """Test that raw bytes data compacts to a base64 data URI."""
        import base64

        raw = b"raw bytes"
        assert (
            compact_attachment({"contentType": "application/pdf", "data": raw})
            == f"data:application/pdf;base64,{base64.b64encode(raw).decode()}"
        )

    def test_dict_hash_and_data_are_invalid(self):
        """Test that dict values for hash and data are invalid Attachment fields."""
        v = {"contentType": "text/plain", "hash": {"dict": 1}, "data": {"dict": 2}}
        with pytest.raises(ValidationError):
            compact_attachment(v)
