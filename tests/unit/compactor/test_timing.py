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

from fhir_mcp_server.compactor.types import Timing


def compact_timing(payload):
    return Timing.model_validate(payload).compact()


class TestCompactTiming:
    """Test direct compact behavior for Timing payloads."""

    def test_code_text_used_verbatim(self):
        """Test that code text is returned as-is."""
        v = {"code": {"text": "Take medication in the morning on weekends"}}
        assert compact_timing(v) == "Take medication in the morning on weekends"

    def test_known_abbreviation_code(self):
        """Test that known timing abbreviation codes are returned as-is."""
        v = {"code": {"coding": [{"code": "BID"}]}}
        assert compact_timing(v) == "BID"

    def test_every_8_hours(self):
        """Test that frequency=1 over 8h period compacts to 'every 8h'."""
        v = {"repeat": {"frequency": 1, "period": 8, "periodUnit": "h"}}
        assert compact_timing(v) == "every 8h"

    def test_3_times_a_day(self):
        """Test that frequency=3 over 1d period compacts to '3x/day'."""
        v = {"repeat": {"frequency": 3, "period": 1, "periodUnit": "d"}}
        assert compact_timing(v) == "3x/day"

    def test_3_to_4_times_a_day(self):
        """Test that frequencyMax produces a range like '3-4x/day'."""
        v = {
            "repeat": {
                "frequency": 3,
                "frequencyMax": 4,
                "period": 1,
                "periodUnit": "d",
            }
        }
        assert compact_timing(v) == "3-4x/day"

    def test_every_4_to_6_hours(self):
        """Test that periodMax produces a range like 'every 4-6h'."""
        v = {"repeat": {"frequency": 1, "period": 4, "periodUnit": "h", "periodMax": 6}}
        assert compact_timing(v) == "every 4-6h"

    def test_every_21_days_for_1_hour(self):
        """Test that duration is appended after the frequency."""
        v = {
            "repeat": {
                "frequency": 1,
                "period": 21,
                "periodUnit": "d",
                "duration": 1,
                "durationUnit": "h",
            }
        }
        assert compact_timing(v) == "every 21d for 1h"

    def test_when_only(self):
        """Test that a when-only repeat expands to the meal/event label."""
        v = {"repeat": {"when": ["CM"]}}
        assert compact_timing(v) == "at breakfast"

    def test_duration_with_offset_and_when(self):
        """Test that duration, offset, and when are all combined."""
        v = {
            "repeat": {
                "duration": 5,
                "durationUnit": "min",
                "when": ["AC"],
                "offset": 10,
            }
        }
        assert compact_timing(v) == "for 5min, 10min before meal"  # AC → "before meal"

    def test_days_of_week_with_when(self):
        """Test that dayOfWeek and when are appended to the frequency."""
        v = {
            "repeat": {
                "frequency": 1,
                "period": 1,
                "periodUnit": "d",
                "dayOfWeek": ["mon", "wed", "fri"],
                "when": ["MORN"],
            }
        }
        assert compact_timing(v) == "1x/day on Mon/Wed/Fri morning"

    def test_time_of_day(self):
        """Test that timeOfDay is appended to the frequency."""
        v = {
            "repeat": {
                "frequency": 1,
                "period": 1,
                "periodUnit": "d",
                "timeOfDay": ["10:00:00"],
            }
        }
        assert compact_timing(v) == "1x/day at 10:00"

    def test_count_only(self):
        """Test that a count-only repeat compacts to 'N time(s)'."""
        v = {"repeat": {"count": 1}}
        assert compact_timing(v) == "1 time"

    def test_event_list(self):
        """Test that explicit event datetimes are joined with commas."""
        v = {"event": ["2012-01-07T09:00:00+10:00", "2012-01-14T09:00:00+10:00"]}
        assert (
            compact_timing(v) == "2012-01-07T09:00:00+10:00, 2012-01-14T09:00:00+10:00"
        )

    def test_multiple_times_per_multi_day_period(self):
        """Test that frequency over a multi-day period compacts to 'Nx/Nd'."""
        v = {"repeat": {"frequency": 2, "period": 3, "periodUnit": "d"}}
        assert compact_timing(v) == "2x/3d"

    def test_bounds_duration(self):
        """Test that boundsDuration is appended as 'for N<unit>'."""
        v = {
            "repeat": {
                "frequency": 2,
                "period": 1,
                "periodUnit": "d",
                "boundsDuration": {
                    "value": 10,
                    "unit": "d",
                    "system": "http://unitsofmeasure.org",
                    "code": "d",
                },
            }
        }
        assert compact_timing(v) == "2x/day for 10d"

    def test_bounds_range(self):
        """Test that boundsRange is appended as 'for low – high'."""
        v = {
            "repeat": {
                "frequency": 3,
                "period": 1,
                "periodUnit": "d",
                "boundsRange": {
                    "low": {"value": 3, "unit": "d"},
                    "high": {"value": 5, "unit": "d"},
                },
            }
        }
        assert compact_timing(v) == "3x/day for 3 d – 5 d"

    def test_bounds_period(self):
        """Test that boundsPeriod is appended as the compacted period string."""
        v = {
            "repeat": {
                "frequency": 2,
                "period": 1,
                "periodUnit": "d",
                "boundsPeriod": {"start": "2015-07-01"},
            }
        }
        assert compact_timing(v) == "2x/day from 2015-07-01"

    def test_when_with_frequency_no_duration(self):
        """Test that when label is appended without duration prefix."""
        v = {
            "repeat": {"frequency": 1, "period": 1, "periodUnit": "d", "when": ["MORN"]}
        }
        assert compact_timing(v) == "1x/day morning"

    def test_duration_with_when_no_offset(self):
        """Test that duration and when are combined without offset."""
        v = {"repeat": {"duration": 5, "durationUnit": "min", "when": ["AC"]}}
        assert compact_timing(v) == "for 5min before meal"

    def test_offset_with_when_no_duration(self):
        """Test that offset and when are combined without duration."""
        v = {"repeat": {"offset": 10, "when": ["AC"]}}
        assert compact_timing(v) == "10min before meal"

    def test_empty_timing_returns_empty_string(self):
        """Test that an empty Timing has no compacted output."""
        assert compact_timing({}) == ""
