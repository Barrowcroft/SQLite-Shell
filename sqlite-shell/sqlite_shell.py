from os import chdir, getcwd
from pprint import pprint
from typing import Any

from commandparser import CommandParser
from commandprocessor import CommandProcessor
from config import Config
from constants import INFO
from database import Database


class SQLiteShell:
    """SQLite Shell

    A simple SQLite shell.
    """

    def __init__(self):
        """__init__

        Initialises the SQLite shell class.
        """

        #  Load configuration settings

        self._config: Config = Config(getcwd())
        self._config.load_config()

        #  Restore saved working directory

        chdir(self._config.get_config("cwd"))

        #  Set up shell

        self._database: Database = Database()
        self._command_parser: CommandParser = CommandParser()
        self._command_processor: CommandProcessor = CommandProcessor(
            self._config, self._database
        )

    def run(self) -> None:
        """run

        Runs the SQLite shell command loop.
        """
        self.show_program_details()

        #  Restore last opened database.

        _database_name: str = self._config.get_config("open")
        if _database_name != "None":
            self._database.open(self._config.get_config("open"))
            print(f"Currently open in database '{_database_name}'.")

        #  Loop until the shell is exited.

        while True:
            #  Initalise sql and results, and get the command string.

            _sql: str = ""
            _results: list[Any] = []

            _command: str = self.get_command_string()

            #  If the command string is not empty process it.

            if _command != "":
                #  If the command string starts with a period then it is a built-in command
                #  and should be prccessed accordingly.

                if _command[0] == ".":
                    #  Parse the command string.
                    (
                        _command,
                        _positional_parameters,
                        _named_parameters,
                    ) = self._command_parser.parse(_command)

                    #  If the command is the exit command then break the loop and exit the shell.

                    if (
                        _command == ".exit"
                        and _positional_parameters == []
                        and _named_parameters == []
                    ):
                        break

                    #  Process the command string. Built-in commands will be executed.
                    #  Some built-in commands may result is sql being returned for execution.

                    _sql = self._command_processor.process(
                        _command, _positional_parameters, _named_parameters
                    )

                else:
                    #  If the command is not a built-in command then it is an sql string ending with a semi-colon.
                    #  Store it for execution.

                    _sql = _command

                #  Execute any pending sql string.

                _results = self._database.execute_sql(
                    _sql,
                    self._config.get_config("echo"),
                )

            self.display_results(_results)

        self.show_program_details()

    def show_program_details(self) -> None:
        """show_program_details

        Prints the program info string
        """
        print(INFO)

    def get_command_string(self) -> str:
        """get_command_string

        If a new string starts with a period it is a built-in command so return it immeiately.

        Otherwise loops while gathering strings and adding them to the sql string to
        be processed. The loop stops when a string is entered that ends with a semi-colon.

        Returns:
            str: command string which is a built-in command or sql.
        """
        _command_string: str = input("Command > ")
        if _command_string != "":
            if _command_string[0] == ".":
                #  This is a built-in command.

                return _command_string
            else:
                #  Construct sql string.

                while not _command_string.endswith(";"):
                    _command_string += " "
                    _command_string += input("        > ")
                return _command_string

        return ""

    def display_results(self, results: list[Any]) -> None:
        """display_results

        Displays the contents of the results list.
        Uses pretty print to format output.

        Args:
            results (list[Any]): results to display.
        """
        for _result in results:
            pprint(_result, width=self._config.get_config("width"))


if __name__ == "__main__":
    _shell = SQLiteShell()
    _shell.run()
