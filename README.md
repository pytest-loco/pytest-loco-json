# pytest-loco-json

JSON extension for `pytest-loco`.

The `pytest-loco-json` extension adds first-class JSON support to the
`pytest-loco` DSL. It provides facilities for decoding, encoding, and
querying JSON data as part of test execution.

This extension is designed to integrate seamlessly with the `pytest-loco`
plugin system and can be enabled by registering the `json` plugin.
Once enabled, JSON becomes a native data format within the DSL, suitable
for validation, transformation, and data-driven testing scenarios.

## Install

```sh
> pip install pytest-loco-json
```

Requirements:
- Python 3.13 or higher

## Documentation

See https://pytest-loco.readthedocs.io/en/latest/extensions/json/index.html

## Thanks

- [Python orjson](https://github.com/ijl/orjson)
- [Python JSONPath](https://jg-rp.github.io/python-jsonpath/)
