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

from fhir_mcp_server.compactor.types import Money


def compact_money(payload):
    return Money.model_validate(payload).compact()


class TestCompactMoney:
    """Test direct compact behavior for Money payloads."""

    def test_value_and_currency(self):
        """Test that value and currency are joined with a space."""
        assert compact_money({"value": 49.99, "currency": "USD"}) == "49.99 USD"

    def test_value_without_currency(self):
        """Test that value alone is returned when currency is absent."""
        assert compact_money({"value": 49.99, "currency": None}) == "49.99"
