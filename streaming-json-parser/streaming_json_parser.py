import unittest

class StreamingJsonParser:
    def __init__(self):
        self.stack = []
        self.current_key = None
        self.current_value = None
        self.in_string = False
        self.partial_string = ""
        self.result = {}
        
    def consume(self, buffer: str):
        actions = {
            '{': lambda: self._handle_start_object(),
            '}': lambda: self._handle_end_object(),
            ':': lambda: self._handle_colon(),
            '"': lambda: self._handle_quote(),
            ',': lambda: self._handle_comma(),
        }

        for char in buffer:
            if char not in actions:
                self._handle_char(char)
            else:
                actions[char]()

    def _handle_start_object(self):
        if not self.stack:
            self.stack.append({})

    def _handle_end_object(self):
        if self.stack:
            if self.current_key and self.current_value is not None:
                self.stack[-1][self.current_key] = self.current_value
            completed_object = self.stack.pop()
            if self.stack:
                if self.current_key:
                    self.stack[-1][self.current_key] = completed_object
                    self.current_key = None
            else:
                if self.current_key and self.current_value is not None:
                    completed_object[self.current_key] = self.current_value
                self.result = completed_object

    def _handle_colon(self):
        pass
    
    def _handle_quote(self):
        if self.in_string:
            if self.current_key is None:
                self.current_key = self.partial_string
            else:
                self.current_value = self.partial_string
            self.partial_string = ""
            self.in_string = False
        else:
            self.in_string = True
            self.partial_string = ""
            
    def _handle_comma(self):
        if self.current_key and self.current_value is not None:
            if self.stack:
                self.stack[-1][self.current_key] = self.current_value
            self.current_key, self.current_value = None, None

    def _handle_char(self, char):
        if self.in_string:
            self.partial_string += char
        elif not self.in_string and char.strip():
            if self.current_value is None:
                self.current_value = char
            else:
                self.current_value += char

    def get(self): 
        if self.current_key and self.current_value is not None and self.stack:
            self.stack[-1][self.current_key] = self.current_value
            self.current_key, self.current_value = None, None
        elif self.current_key is not None and self.current_value is None and self.stack:
            self.stack[-1][self.current_key] = self.partial_string
            self.current_key, self.current_value = None, None
        if self.result == {} and self.stack is not None:
            self.result = self.stack.pop()
        return self.result

class TestStreamingJsonParser(unittest.TestCase):
    def test_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{"foo": "bar"}')
        assert parser.get() == {"foo": "bar"}

    def test_chunked_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{"foo":')
        parser.consume('"bar')
        assert parser.get() == {"foo": "bar"}

    def test_chunked_key_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{"fo')
        parser.consume('o": "bar"}')
        assert parser.get() == {"foo": "bar"}
    
    def test_chunked_value_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{"foo": "b')
        parser.consume('ar"')
        assert parser.get() == {"foo": "bar"}

    def test_partial_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{"foo": "bar')
        assert parser.get() == {"foo": "bar"}

    def test_partial_key_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{"test": "hello", "worl')
        assert parser.get() == {"test": "hello"}

    def test_opening_bracket_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{')
        assert parser.get() == {}
    
    def test_key_without_value_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{"tes"')
        assert parser.get() == {"tes": ""}

    def test_nested_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{"foo": {"foo":"bar"}}')
        assert parser.get() == {"foo": {"foo":"bar"}}

if __name__ == '__main__':
    unittest.main()