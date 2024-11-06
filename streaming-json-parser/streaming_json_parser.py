import unittest


class StreamingJsonParser:
    def __init__(self):
        """
        Initializes a StreamingJsonParser object.

        The object is initialized with empty stack, no current key or value,
        not in a string, no partial string, and an empty result.
        """
        self.stack = []
        self.current_key = None
        self.current_value = None
        self.in_string = False
        self.partial_string = ""
        self.result = {}

    def consume(self, buffer: str):
        """
        Consumes a string buffer and attempts to parse it.

        The buffer is parsed by iterating through the characters in the buffer.
        For each character, if it is a special character, it is handled by
        calling the corresponding method. If the character is not special, it is
        handled by calling the _handle_non_special_character method.

        :param buffer: The string buffer to be parsed
        """
        actions = {
            '{': lambda: self._handle_start_object(),
            '}': lambda: self._handle_end_object(),
            ':': lambda: self._handle_colon(),
            '"': lambda: self._handle_quote(),
            ',': lambda: self._handle_comma(),
        }

        for char in buffer:
            if char not in actions:
                # If the character is not special, handle it
                self._handle_non_special_character(char)
            else:
                # If the character is special, call the corresponding method
                actions[char]()

    def _handle_start_object(self):
        """
        Handles a '{' character in the input buffer.

        When the '{' character is encountered, if the stack is empty, a new
        object is created and pushed onto the stack.
        """
        if not self.stack:
            self.stack.append({})

    def _handle_end_object(self):
        """
        Handles a '}' character in the input buffer.

        This method finalizes the most recently opened JSON object. If there is a
        current key and value, they are added to the stack. The completed object is
        then popped from the stack. If there are still objects on the stack, the
        completed object is assigned to the current key of the next object in the
        stack. If the stack is empty, the completed object becomes the result.
        """
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
        """
        Handles a '"' character in the input buffer.

        If the parser is in a string (i.e. self.in_string is True), the
        current key or value is set to the partial string and the partial
        string is reset. If the parser is not in a string, the parser is
        set to be in a string and the partial string is reset.
        """
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
        """
        Handles a ',' character in the input buffer.

        If the current key and value are not None, they are added to the
        current object in the stack. The current key and value are then reset.
        """
        if self.current_key and self.current_value is not None:
            if self.stack:
                self.stack[-1][self.current_key] = self.current_value
            self.current_key, self.current_value = None, None

    def _handle_non_special_character(self, char):
        """
        Handles a non-special character in the input buffer.

        If the parser is in a string (i.e. self.in_string is True), the
        character is added to the partial string. If the parser is not in a
        string, the character is added to the current value if it is not
        None, otherwise it is set as the current value.
        """
        if self.in_string:
            self.partial_string += char
        elif not self.in_string and char.strip():
            if self.current_value is None:
                self.current_value = char
            else:
                self.current_value += char

    def get(self) -> dict:
        """
        Returns the parsed JSON object as a dictionary.

        The method checks if there are any remaining key-value pairs or
        strings that need to be added to the result. It then returns the
        result.

        :return: The parsed JSON object as a dictionary
        """
        if self.current_key and self.current_value is not None and self.stack:
            self.stack[-1][self.current_key] = self.current_value
            self.current_key, self.current_value = None, None
        elif self.current_key is not None and self.current_value is None and self.stack:
            self.stack[-1][self.current_key] = self.partial_string
            self.current_key, self.current_value = None, None
        if self.result == {} and self.stack:
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
        parser.consume("{")
        assert parser.get() == {}

    def test_key_without_value_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('{"tes"')
        assert parser.get() == {"tes": ""}

    def test_suffix_streaming_json_parser(self):
        parser = StreamingJsonParser()
        parser.consume('ar"}')
        assert parser.get() == {}


if __name__ == "__main__":
    unittest.main()
