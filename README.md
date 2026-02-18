# pytest-loco-json

JSON extension for `pytest-loco`.

The `pytest-loco-json` extension adds first-class JSON support to the
`pytest-loco` DSL. It provides facilities for decoding, encoding, and
querying JSON data as part of test execution.

This extension is designed to integrate seamlessly with the `pytest-loco`
plugin system and can be enabled by registering the `json` plugin.
Once enabled, JSON becomes a native data format within the DSL, suitable
for validation, transformation, and data-driven testing scenarios.

## Encode

The **dump** feature serializes a value from the execution context into a
JSON string using the high-performance `orjson` backend.

Encoding is typically used when preparing request payloads, exporting
structured data, or normalizing values for comparison. The encoder
accepts an optional `sortKeys` parameter that controls serialization
behavior and enables deterministic key ordering.

Encoded values are returned as UTF-8 JSON strings and can be passed
directly to actions (for example, HTTP requests) or stored in the
execution context.

For example:

```yaml
---
spec: case
title: Example of encoding a value
vars:
  value:
    name: Molecule Man
    secretIdentity: Dan Jukes
    age: 29

---
action: pass
export:
  jsonText: !dump
    source: !var value
    format: json
```

The result of executing this case will be the assignment of the
following value (without indentation) to the variable `jsonText`:

```json
{
  "name": "Molecule Man",
  "age": 29,
  "secretIdentity": "Dan Jukes"
}
```

Optionally, you can use the `sortKeys` option:

```yaml
...
action: pass
export:
  jsonText: !dump
    source: !var value
    format: json
    sortKeys: yes
```

In this case, the keys will be sorted alphabetically:

```json
{
  "age": 29,
  "name": "Molecule Man",
  "secretIdentity": "Dan Jukes"
}
```

## Decode

The **load** feature parses a JSON string into native Python objects and
stores them as values in the execution context.

Decoding allows JSON payloads to become fully addressable within the
DSL execution context. Once decoded, values can be inspected, exported,
validated, or transformed by subsequent steps.

Decoder parameters are intentionally minimal: decoding focuses on
correctness and performance, while transformation logic is handled
separately.

For example:

```yaml
---
spec: case
title: Example of decoding a value

---
action: pass
title: Read JSON content from file
export:
  jsonText: !textFile test.json

---
action: pass
title: Try to decode JSON
export:
  jsonValue: !load
    source: !var jsonText
    format: json
```

The result of executing this case will be the assignment of the decoded
JSON object to the variable `jsonValue`.

## Transform by JSONPath

The **load** feature can be extended with an optional transformer that
enables extracting data from decoded JSON structures using JSONPath
expressions.

Transforms are applied after decoding and allow selecting either a
single value or multiple values from complex, deeply nested documents.
Behavior is configurable to return the first match, the last match, or
a full list of matches.

This makes it possible to work with large or variable JSON payloads
without hard-coding structural assumptions into the test logic.

Use the following `test.json` file contents as an example:

```json
[
  {
    "name": "Molecule Man",
    "age": 29,
    "secretIdentity": "Dan Jukes",
    "powers": [
      "Radiation resistance",
      "Turning tiny",
      "Radiation blast"
    ]
  },
  {
    "name": "Madame Uppercut",
    "age": 39,
    "secretIdentity": "Jane Wilson",
    "powers": [
      "Million tonne punch",
      "Damage resistance",
      "Superhuman reflexes"
    ]
  }
]
```

Optionally, you can use the `query` transformer with **load**:

```yaml
...

action: pass
title: Decode JSON and select the first match
export:
  jsonValue: !load
    source: !var jsonText
    format: json
    query: '$[*].name'
expect:
- title: Check first selected name
  value: !var jsonValue
  match: Molecule Man
```

By default, the first match of the JSONPath query is selected.
This behavior can be controlled using the `exactOne` parameter
(`true` or `false`; when `false`, the query returns a full list of
matches) and the `exactMode` parameter (`first` or `last` on a
single mode querying).

For example:

```yaml
...

action: pass
title: Try to decode JSON and select all
export:
  jsonValue: !load
    source: !var jsonText
    format: json
    query: '$[?(@.age<30)].powers[*]'
    exactOne: no
expect:
- title: Check result is list of powers
  value: !var jsonValue
  match:
  - Radiation resistance
  - Turning tiny
  - Radiation blast
```

## Inline querying

Inline querying allows JSONPath expressions to be defined directly
inside the DSL using the dedicated `!jsonpath` instruction.

Inline queries are compiled during schema loading rather than at runtime,
which improves error reporting and ensures invalid paths fail early.
Compiled queries can be stored in variables and reused across steps.

This feature is especially useful for complex test suites where the
same JSONPath expressions appear in multiple places, or when clarity
and reuse are more important than brevity.

For example:

```yaml
---
action: pass
title: Try to select from context by instruction
export:
  resultValues: !jsonpath jsonValue $[?(@.age<_.ageLimit)].powers[*]
expect:
- title: Check result is list of powers
  value: !var resultValues
  match:
  - Radiation resistance
  - Turning tiny
  - Radiation blast
```

The result is always a list.
