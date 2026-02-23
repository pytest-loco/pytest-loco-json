"""JSON content type support.

This module defines JSON decoding and encoding support for the DSL,
based on the `orjson` library. It also integrates JSONPath-based
transformations to allow querying decoded JSON structures.
"""

from functools import cache
from typing import TYPE_CHECKING

import orjson

from pytest_loco.extensions import (
    Attribute,
    ContentDecoder,
    ContentEncoder,
    ContentType,
    Schema,
)

from .transforms import query

if TYPE_CHECKING:
    from collections.abc import Mapping

if TYPE_CHECKING:
    from pytest_loco.values import RuntimeValue


@cache
def _json_decode(value: bytes | str) -> 'RuntimeValue':
    """Decode a JSON document with caching."""
    if not isinstance(value, (bytes, str)):
        raise TypeError('wrong type to decode')

    return orjson.loads(value)


def json_decode(value: 'RuntimeValue',
                params: 'Mapping[str, RuntimeValue]') -> 'RuntimeValue':  # noqa: ARG001
    """Decode a JSON string into a Python value.

    This decoder parses a JSON document into native Python objects
    using `orjson`. Decoding results are cached for reuse.
    Decoder parameters are ignored.

    Args:
        value: JSON string to decode.
        params: Decoder parameters (unused).

    Returns:
        Parsed Python representation of the JSON document.
    """
    return _json_decode(value)


def json_encode(value: 'RuntimeValue',
                params: 'Mapping[str, RuntimeValue]') -> str:
    """Encode a Python value into a JSON string.

    This encoder serializes a Python value into JSON using `orjson`.
    Optional parameters control serialization behavior.

    Args:
        value: Python value to serialize.
        params: Encoder parameters.

    Returns:
        JSON string representation of the value.
    """
    options = 0
    if params.get('sort'):
        options |= orjson.OPT_SORT_KEYS

    return orjson.dumps(value, option=options).decode()


json_decoder = ContentDecoder(
    decoder=json_decode,
    transformers=[
        query,
    ],
)

json_encoder = ContentEncoder(
    encoder=json_encode,
    parameters=Schema({
        'sort': Attribute(
            base=bool,
            aliases=['sortKeys'],
            default=False,
            deferred=False,
            title='Sort JSON object keys',
            description=(
                'If enabled, JSON object keys are sorted alphabetically '
                'during serialization.'
            ),
        ),
    }),
)

json_format = ContentType(
    name='json',
    decoder=json_decoder,
    encoder=json_encoder,
)
