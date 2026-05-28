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
Pydantic Tagged Union and custom discriminator routing configuration for FHIR General-Purpose types.
"""

from typing import Any, Union, Annotated
from pydantic import Discriminator, TypeAdapter, Tag

from fhir_mcp_server.compactor.types import (
    Address,
    Annotation,
    Attachment,
    CodeableConcept,
    Coding,
    ContactPoint,
    Extension,
    HumanName,
    Identifier,
    Money,
    Period,
    Quantity,
    Range,
    Ratio,
    Reference,
    Timing,
)


def fhir_type_discriminator(v: Any) -> str:
    """Discriminator mapping dictionaries to their corresponding FHIR type tags.
    
    Routes structures by matching unique field combinations to avoid sequential 
    validation loops.
    """
    if not isinstance(v, dict):
        return "pass_through"

    keys = set(v.keys())

    # 1. Simple unique structural signatures
    if "currency" in keys:
        return "Money"
    if "numerator" in keys or "denominator" in keys:
        return "Ratio"
    if "low" in keys or "high" in keys:
        return "Range"
    if "start" in keys or "end" in keys:
        return "Period"
    if "authorString" in keys or "authorReference" in keys:
        return "Annotation"
    if "creation" in keys or "size" in keys or "contentType" in keys:
        return "Attachment"
    if "event" in keys or "repeat" in keys:
        return "Timing"

    # 2. HumanName vs Address (both can share use/period/text)
    if any(k in keys for k in ("given", "family", "prefix", "suffix")):
        return "HumanName"
    if any(k in keys for k in ("line", "city", "state", "postalCode", "country", "district")):
        return "Address"
    if "use" in keys and "text" in keys:
        return "HumanName"

    # 3. Polymorphic URL payloads (Extension vs Attachment)
    if "url" in keys:
        is_extension = "extension" in keys or any(k.startswith("value") for k in keys)
        is_url_only = len(keys - {"url", "id"}) == 0
        if is_extension or is_url_only:
            return "Extension"
        return "Attachment"

    # 4. Overlapping 'value' key payloads (Quantity vs Identifier vs ContactPoint)
    if "value" in keys:
        if any(k in keys for k in ("unit", "code", "comparator")):
            return "Quantity"
        
        if "system" in keys:
            system_val = str(v.get("system") or "")
            if "http" in system_val or "urn:" in system_val:
                return "Identifier"
            return "ContactPoint"
        
        if "use" in keys:
            return "ContactPoint"

        return "Quantity"

    # 5. Core reference and concept models
    if "reference" in keys:
        return "Reference"
    
    if "display" in keys:
        if any(k in keys for k in ("code", "system")):
            return "Coding"
        return "Reference"

    if "coding" in keys or "text" in keys:
        return "CodeableConcept"

    if "code" in keys or "system" in keys:
        return "Coding"

    return "pass_through"


FhirComplexUnion = Annotated[
    Union[
        Annotated[Money, Tag("Money")],
        Annotated[Range, Tag("Range")],
        Annotated[Ratio, Tag("Ratio")],
        Annotated[Period, Tag("Period")],
        Annotated[Annotation, Tag("Annotation")],
        Annotated[Attachment, Tag("Attachment")],
        Annotated[Timing, Tag("Timing")],
        Annotated[HumanName, Tag("HumanName")],
        Annotated[Address, Tag("Address")],
        Annotated[Extension, Tag("Extension")],
        Annotated[Quantity, Tag("Quantity")],
        Annotated[ContactPoint, Tag("ContactPoint")],
        Annotated[Identifier, Tag("Identifier")],
        Annotated[Reference, Tag("Reference")],
        Annotated[CodeableConcept, Tag("CodeableConcept")],
        Annotated[Coding, Tag("Coding")],
        Annotated[dict, Tag("pass_through")],
    ],
    Discriminator(fhir_type_discriminator),
]

COMPACTOR_ADAPTER = TypeAdapter(FhirComplexUnion)
