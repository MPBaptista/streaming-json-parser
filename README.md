# streaming-json-parser
A lightweight streaming JSON parser implemented in Python.

## Table of Contents
- [Usage](#usage)
- [Limitations](#limitations)
- [License](#license)

## Usage
```python
    parser = StreamingJsonParser() # initialize the parser
    parser.consume('{"foo": "bar') # consume data
    parser.get() == {}             # get the parsed json data
```

## Limitations
Currently, the parser doesn't support nested dictionaries. Feature will be added in the future.

## License
This repository is licensed under the MIT License. See the LICENSE file for details.