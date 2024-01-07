from os import chdir, getcwd, listdir, system
from typing import Any

from config import Config
from constants import HELP_TEXT
from database import Database


class CommandProcessor:
    def __init__(self, config: Config, database:Database) -> None:
        """__init__

        Initialises command processor class.
        """
        #  Store the configuration and database.

        self._config = config
        self._database = database

        #  Set up the dictionaries of built-in commands with their methods.
        #  There are two types of command; those that execute immediately and those
        #  that return an sql string to be executed later.

        #  Set up immediate commands. Dictionary entries consit of the expected parameter count
        #  and the method to call to execute the command.

        self._immediate_command_list: dict[str, tuple[int, Any]] = {}
        self._immediate_command_list[".close"] = (0, self.command_close)
        self._immediate_command_list[".create"] = (1, self.command_create)
        self._immediate_command_list[".cwd"] = (1, self.command_cwd)
        self._immediate_command_list[".delete"] = (1, self.command_delete)
        self._immediate_command_list[".dir"] = (0, self.command_dir)
        self._immediate_command_list[".echo"] = (1, self.command_echo)
        self._immediate_command_list[".edit"] = (0, self.command_edit)
        self._immediate_command_list[".exit"] = (1, self.command_exit)
        self._immediate_command_list[".help"] = (0, self.command_help)
        self._immediate_command_list[".open"] = (1, self.command_open)
        self._immediate_command_list[".script"] = (1, self.command_script)
        self._immediate_command_list[".width"] = (1, self.command_width)

        #  Set up commands that return sql. Dictionary entries consit of the expected parameter count
        #  and the sql string to execute once parameters have been added in.

        self._sql_command_list: dict[str, tuple[int, str]] = {}
        self._sql_command_list[".describe"] = (
            1,
            "SELECT sql FROM sqlite_schema WHERE name = ?;",
        )
        self._sql_command_list[".schema"] = (0, "SELECT sql FROM sqlite_schema")
        self._sql_command_list[".tables"] = (
            0,
            "SELECT name FROM sqlite_schema WHERE type = 'table' AND name NOT LIKE 'sqlite_%';",
        )

    def process(
        self,
        command: str,
        positional_parameters: list[str | int],
        named_parameters: list[dict[str, Any]],
    ) -> str:
        """process

        Processes the command.

        Args:
            command (str): command to process.
            positional_parameters (list[str  |  int]): list of positional parameters.
            named_parameters (list[dict[str, Any]]): list of named parameters.

        Returns:
            str: sql produced by commands.
        """
        #  Initialise variables

        _command_matched: bool = False
        _sql: str = ""

        #  Process immediate commands. Match from list and then
        #  verify that the correct number of parameters have been provided
        #  amd execute appropriate method.

        if command in self._immediate_command_list.keys():
            _command_matched = True

            if self.check_parameter_count(
                command,
                self._immediate_command_list[command][0],
                positional_parameters,
                named_parameters,
            ):
                _sql = self.execute_immediate_command(
                    command, positional_parameters, named_parameters
                )

        #  Process command that returns sql.

        if command in self._sql_command_list.keys():
            _command_matched = True

            if self.check_parameter_count(
                command,
                self._sql_command_list[command][0],
                positional_parameters,
                named_parameters,
            ):
                _sql = self.construct_sql_command(
                    command, positional_parameters, named_parameters
                )

        #  If the command has not been matched report an error.

        if not _command_matched:
            print(f"Error: command not found - {command}.")

        return _sql

    def check_parameter_count(
        self,
        command: str,
        expected_num_of_positional_parameters: int,
        positional_parameters: list[str | int],
        named_parameters: list[dict[str, Any]],
    ) -> bool:
        """check_parameter_count

        Args:
            command (str): command
            expected_num_of_positional_parameters (int): as described.
            positional_parameters (list[str  |  int]): list of positional parameters.
            named_parameters (list[dict[str, Any]]): list of named parameters.

        Returns:
            bool: indicates if the correct number of parameters were supplied.
        """
        #  First deal with the special case of '.script'.
        #  To check the paramters on the '.script' command we can only check that there is
        #  at least one paramter, the script to execute. Other paramters are ignored for now
        #  as we dont know, at this point, how many parameters the script will require

        if command == ".script":
            if len(positional_parameters) < 1:
                print(
                    f"Error: incorrect number of positional parameters. The current command uses at least one (the script to execute), and there are none supplied."
                )
                return False
            if len(positional_parameters) > 2 and positional_parameters[1]=="?":
                print(
                    f"Error: incorrect number of parameters. No parameters are expected after '?'."
                )   
                return False             
            else:
                return True

        #  Check the number of expected parameters

        _expected_num_of_positional_parameters = expected_num_of_positional_parameters
        _expected_num_of_named_parameters = 0

        #  Check the number of actual paramters

        _actual_num_of_positional_parameters = len(positional_parameters)
        _actual_num_of_named_parameters = len(named_parameters)

        #  If the number of actual parameters is not the same as the expected number
        #  then report an error.

        if (
            _expected_num_of_positional_parameters
            != _actual_num_of_positional_parameters
        ):
            print(
                f"Error: incorrect number of positional parameters. The current command uses {_expected_num_of_positional_parameters}, and there are {_actual_num_of_positional_parameters} supplied."
            )
            return False

        if _actual_num_of_named_parameters != _expected_num_of_named_parameters:
            print(
                f"Error: incorrect number of named parameters. The current command uses {_actual_num_of_named_parameters}, and there are {_expected_num_of_named_parameters} supplied."
            )
            return False

        return True

    def execute_immediate_command(
        self,
        command: str,
        positional_parameters: list[str | int],
        named_parameters: list[dict[str, Any]],
    ) -> str:
        """execute_immediate_command

        Executes the immediate (built-in) commands.

        Args:
            command (str): command to execute
            positional_parameters (list[str  |  int]): list of positional parameters.
            named_parameters (list[dict[str, Any]]): list of named parameters.

        Returns:
            str: sql produced by commands.
        """
        #  Get the command method to call. Call it with the positional parameter list.

        _command = self._immediate_command_list[command][1]
        _sql: str = _command(positional_parameters, named_parameters)

        return _sql

    def construct_sql_command(
        self,
        command: str,
        positional_parameters: list[str | int],
        named_parameters: list[dict[str, Any]],
    ) -> str:
        """construct_sql_command

        COnstructs the sql command by retieving the sql and adding in the provided parameters.

        Args:
            command (str): command to execute
            positional_parameters (list[str  |  int]): list of positional parameters.
            named_parameters (list[dict[str, Any]]): list of named parameters.

        Returns:
            str: sql produced by commands.
        """
        #  Get the sql string to execute.

        _sql: str = self._sql_command_list[command][1]

        #  Substitute any question marks for positional parameters.

        if "?" in _sql:
            for _index in range(len(positional_parameters)):
                _sql = _sql.replace("?", f"'{positional_parameters[_index]}'", 1)

        #  Return sql string.

        return _sql

    #  Methods to implement built-in commands.

    def command_close(self, positional_parameters: list[str], named_parameters: list[dict[str, Any]]
    ) -> str:
        """command_close

        Closes the currently open database.

        Args:
            positional_parameters (list[str]): list of positional parameters, ignored.
            named_parameters (list[dict[str, Any]]): list of named parameters, ignored.

        Returns:
            str: empty string.
        """
        if self._database.close():
            self._config.set_config("open", "None")

        return ""
    
    def command_create(self, positional_parameters: list[str], named_parameters: list[dict[str, Any]]
    ) -> str:
        """command_create

        Creates a database. Defaults to current working directory if a path is not given.

        Args:
            positional_parameters (list[str]): name (and path) of database to create.
            named_parameters (list[dict[str, Any]]): named parameters, ignored.

        Returns:
            str: empty string.
        """
        self._database.create(positional_parameters[0])

        return ""


    def command_cwd(
        self, positional_parameters: list[str], named_parameters: list[dict[str, Any]]
    ) -> str:
        """command_cwd

        Changes the current working directory. If a question mark is passed as a parameter
        rather than a new directory the current working directory is printed.

        Args:
            positional_parameters (list[str]): directory to change to, or ?.
            named_parameters (list[dict[str, Any]]): list of named parameters, ignored.

        Returns:
            str: empty string.
        """
        if positional_parameters[0] == "?":
            print(f"Current working directory is {self._config.get_config("cwd")}")
        else:

            try:
                chdir(positional_parameters[0])
                self._config.set_config("cwd", getcwd())

            except OSError as error:
                print(f"Error: {error}.")

        return ""


    def command_delete(
        self, positional_parameters: list[str], named_parameters: list[dict[str, Any]]
    ) -> str:
        """command_delete

        Deletes a specified database.

        Args:
            positional_parameters (list[str]): list of positional parameters, ignored.
            named_parameters (list[dict[str, Any]]): list of named parameters, ignored.

        Returns:
            str: empty string.
        """
        if self._config.get_config("open").lower().strip() == positional_parameters[0].lower().strip():
            print(f"Error: cannot delete currently open database.")
        else:
            if self._database.delete(positional_parameters[0]):
                self._config.set_config("open", "None")

        return ""

    def command_dir(
        self, positional_parameters: list[str], named_parameters: list[dict[str, Any]]
    ) -> str:
        """command_dir

        Displays the contents of the current working directory.

        Args:
            positional_parameters (list[str]): list of positional parameters, ignored.
            named_parameters (list[dict[str, Any]]): list of named parameters, ignored.

        Returns:
            str: empty string.
        """
        try:
            _dir: str = getcwd()
            _list = listdir(_dir)
            for _item in _list:
                print(_item)

        except FileNotFoundError as error:
            print(f"Error: {error}.")

        return ""


    def command_echo(
        self, positional_parameters: list[str], named_parameters: list[dict[str, Any]]
    ) -> str:
        """command_echo

        Set the echo flag. If on the sql is echod before being executed.
        If a question mark is passed as the parameter the current status of the echjo flag is printed.

        Args:
            positional_parameters (list[str]): on/off, or ?.
            named_parameters (list[dict[str, Any]]): list of named parameters, ignored.

        Returns:
            str: empty string.
        """
        if positional_parameters[0].lower().strip() == "on":
            self._config.set_config("echo", "ON")

        if positional_parameters[0].lower().strip() == "off":
            self._config.set_config("echo", "OFF")

        if positional_parameters[0].lower().strip() == "?":
            print(f"Echo is {self._config.get_config("echo")}")

        return ""

    def command_edit(
        self, positional_parameters: list[str], named_parameters: list[dict[str, Any]]
    ) -> str:
        """command_edit

        Opens the system editr.

        Args:
            positional_parameters (list[str  |  int]): list of positional parameters, ignored.
            named_parameters (list[dict[str, Any]]): list of named parameters, ignored.

        Returns:
            str: empty string.
        """
        system('notepad.exe')
        return ""

    def command_exit(
        self, positional_parameters: list[str], named_parameters: list[dict[str, Any]]
    ) -> str:
        """command_exit

        Does nothing. Just a place holder so that all internal commands can be treated the same"

        Args:
            positional_parameters (list[str]): list of positional parameters, ignored.
            named_parameters (list[dict[str, Any]]): list of named parameters, ignored.

        Returns:
            str: empty string.
        """
        return ""

    def command_help(
        self, positional_parameters: list[str], named_parameters: list[dict[str, Any]]
    ) -> str:
        """command_help

        Prints the help text.

        Args:
            positional_parameters (list[str]): list of positional parameters, ignored.
            named_parameters (list[dict[str, Any]]): list of named parameters, ignored.

        Returns:
            str: empty string.
        """
        print(HELP_TEXT)

        return ""

    def command_open(
        self, positional_parameters: list[str], named_parameters: list[dict[str, Any]]
    ) -> str:
        """command_open

        Opens a database. Defaults to current working directory if a path is not given.

        Args:
            positional_parameters (list[str]): name (and path) of database to open.
            named_parameters (list[dict[str, Any]]): list of named parameters, ignored.

        Returns:
            str: empty string.
        """
        if positional_parameters[0] == "?":
            if self._config.get_config("open") != "None":
                print(f"Currently open database is '{self._config.get_config("open")}'")
            else:
                print(f"There is no database open")
        else:
            if self._database.open(positional_parameters[0]):
                self._config.set_config("open", str(positional_parameters[0]))

        return ""


    def command_script(
        self, positional_parameters: list[str], named_parameters: list[dict[str, Any]]
    ) -> str:
        """command_execute

        Loads an sql script from the given file. The method processes the built-in
        .script command, but does not actually execute the sql at this point.
        The sql is loaded from the file and positional and named parameters are
        are substituted into the sql string.

        If the parameter after the script filename (the second parameter) is a question mark
        then rather than prepare the script for execution is it just printed out.

        Args:
            positional_parameters (list[str]): positional parameters to incorporate into sql string.
            named_parameters (list[dict[str, Any]]): named parameters to incorporate into sql string.

        Returns:
            str: sql string passed back for execution.
        """
        _sql: str = self.load_sql_script(positional_parameters[0])

        if len(positional_parameters) == 2 and positional_parameters[1] == "?" and _sql != "":
            print(_sql)
            _sql = ""

        if _sql != "":
            #  Substitute any question marks for positional parameters.

            if "?" in _sql:
                for _index in range(len(positional_parameters)):
                    _sql = _sql.replace("?", f"'{positional_parameters[_index]}'", 1)

            #  Subsitute named paramters for appropriate values.

            for _named_parameter in named_parameters:
                for key in _named_parameter.keys():
                    if f":{key}" in _sql:
                        _sql = _sql.replace(f":{key}", str(_named_parameter[key]), 1)
                    else:
                        if self._config.get_config("echo") == "ON":
                            print(_sql)
                        print(
                            f"Error: named parameter '{key}' supplied to but not required."
                        )
                        _sql = ""

        return _sql


    def command_width(
        self, positional_parameters: list[str], named_parameters: list[dict[str, Any]]
    ) -> str:
        """command_width

        Set the width for the pretty printed output.
        If a question mark is passed as the parameter the current width is printed.

        Args:
            positional_parameters (list[str]): print width, or ?.
            named_parameters (list[dict[str, Any]]): list of named parameters, ignored.

        Returns:
            str: empty string.
        """
        if positional_parameters[0] == "?":
            print(f"Width is {self._config.get_config("width")}")
        else:
            try:
                self._config.set_config("width", str(positional_parameters[0]))
            except ValueError:
                print("Error: expected integer value 'width'.")

        return ""

    #  Helper methods.

    def load_sql_script(self, script: str) -> str:
        """load_sql_script

        Loads an sql script from a file.

        Args:
            script (str): name of file containing script.

        Returns:
            str: script sql.
        """
        try:
            with open(script, "r") as file:
                _sql_string: str = file.read()
                return _sql_string
        except FileNotFoundError as error:
            print(f"Error: {error}.")
            return ""
