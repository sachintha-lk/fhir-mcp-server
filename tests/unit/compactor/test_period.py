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

from datetime import date, datetime
from fhir_mcp_server.compactor.types import Period


def compact_period(payload):
    return Period.model_validate(payload).compact()


class TestCompactPeriodInputTypes:
    """Test direct compact behavior for Period using Python date/datetime inputs."""

    def test_date_objects_compact(self):
        """Test that Python date objects compact to ISO date strings."""
        assert (
            compact_period({"start": date(2024, 1, 1), "end": date(2024, 6, 1)})
            == "2024-01-01 – 2024-06-01"
        )

    def test_equal_start_end_compact(self):
        """Test that equal start and end dates compact to a range."""
        assert (
            compact_period({"start": "2024-01-01", "end": "2024-01-01"})
            == "2024-01-01 – 2024-01-01"
        )

    def test_datetime_objects_compact(self):
        """Test that Python datetime objects compact to ISO datetime strings."""
        assert (
            compact_period(
                {"start": datetime(2024, 1, 1, 10), "end": datetime(2024, 1, 1, 12)}
            )
            == "2024-01-01 10:00:00 – 2024-01-01 12:00:00"
        )


class TestCompactPeriod:
    """Test direct compact behavior for Period payloads."""

    def test_start_and_end(self):
        """Test that start and end are joined with an en-dash."""
        assert (
            compact_period({"start": "2024-01-01", "end": "2024-06-30"})
            == "2024-01-01 – 2024-06-30"
        )

    def test_only_start(self):
        """Test that a start-only period is prefixed with 'from'."""
        assert compact_period({"start": "2024-01-01"}) == "from 2024-01-01"

    def test_only_end(self):
        """Test that an end-only period is prefixed with 'until'."""
        assert compact_period({"end": "2024-06-30"}) == "until 2024-06-30"
