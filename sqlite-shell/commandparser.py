from shlex import split
from typing import Any


class CommandParser:
    """parser

    Provides parsing function.
    """

    def __init__(self) -> None:
        """__init__

        Initialises parser class.
        """
        self.command: str = ""
        self.positional_parameters: list[str | int] = []
        self.named_parameters: list[dict[str, Any]] = []

    def parse(
        self, command_string: str
    ) -> tuple[str, list[str | int], list[dict[str, Any]]]:
        """parse

        Parses a given string. The string is parsed into a command, and a list of positional arguments
        and a list of named arguments. The named arguments are returned as dictionaries.
        Strings that can be converted to integers or floats will be so converted.

        Args:
            command_string (str): string to parse

        Returns:
            tuple[str, list[str | int], list[dict[str, Any]]]: retuned command, list of positional parameters and list of name parameters.
        """

        #  Clear variables.

        self.command = ""
        self.positional_parameters = []
        self.named_parameters = []

        if len(command_string) > 0:
            #  Split command string into parts and extract first part as the command.
            #  The split uses the shlex.split to preserve paramters enclosd with quotation marks.

            _command_string_parts = split(command_string)
            self.command = _command_string_parts[0].lower().strip()

            #  Loop over remaining parts.

            if len(_command_string_parts) > 1:
                _parameters: list[str] = _command_string_parts[1:]

                for _parameter in _parameters:
                    #  If the parameter does not contain a colon then it is a positional parameter,
                    #  so convert to int or float if possible and store in list of positional parameters.

                    if ":" not in _parameter:
                        self.positional_parameters.append(self.convert(_parameter))

                    else:
                        #  If the colon is present then the parameter is a named parameter. Split it at the colon and
                        #  store the two parts and key and value in a dictionary. Store dictionary in list of named paramters.
                        _key, _value = _parameter.split(":")

                        _named_parameter: dict[str, Any] = {}
                        _named_parameter[_key] = self.convert(_value)

                        self.named_parameters.append(_named_parameter)

        #  Return results of parsing the command string. Results will also be available as properties of the parser object.

        return self.command, self.positional_parameters, self.named_parameters

    def convert(self, parameter: Any) -> Any:
        """convert

        Convert a string to integer or float. Returns the original string if it cannot be converted.

        Args:
            parameter (Any): string to convert.

        Returns:
            Any: converted string or original string.
        """
        _converters = [int, float]

        #  Try to convert parameter to int, if that fails try to convert to float.
        #  If both fail return original.

        for _converter in _converters:
            try:
                return _converter(parameter)
            except ValueError:
                continue

        return parameter
