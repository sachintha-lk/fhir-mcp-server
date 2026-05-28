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
Token-efficient compaction of FHIR General-Purpose Data Types.

Traverses JSON dictionaries recursively and utilizes a pre-compiled
Pydantic TypeAdapter to validate and compact matched types in place.
"""

from typing import Any
from pydantic import ValidationError
from fhir_mcp_server.compactor.discriminator import COMPACTOR_ADAPTER


def compact_datatypes(data: Any) -> Any:
    """Recursively compact FHIR General-Purpose Data Types in a FHIR response payload.

    Handled: Coding, CodeableConcept, Quantity (including subtypes Age/Count/Distance/Duration/
    MoneyQuantity/SimpleQuantity), Range, Ratio, Period, HumanName, Address, ContactPoint,
    Identifier, Attachment, Annotation, Money, Timing, Extension.
    """
    if isinstance(data, list):
        return [compact_datatypes(item) for item in data]
    if not isinstance(data, dict):
        return data

    try:
        matched_obj = COMPACTOR_ADAPTER.validate_python(data)
        if isinstance(matched_obj, dict):
            return {key: compact_datatypes(value) for key, value in data.items()}
            
        result = matched_obj.compact()
        return result if result else data
    except ValidationError:
        return {key: compact_datatypes(value) for key, value in data.items()}
