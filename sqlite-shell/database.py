from os import path, remove
from sqlite3 import (
    Connection,
    Cursor,
    Error,
    IntegrityError,
    OperationalError,
    ProgrammingError,
    connect,
)
from typing import Any


class Database:
    """database

    Provides database functions.
    """

    def __init__(self) -> None:
        """__init__

        Initialises database class.
        """
        self._conn: Connection
        self._cur: Cursor

        self._results: list[Any] = []

    def create(self, filename: str) -> bool:
        """create

        Creates and connects to a new database.

        Args:
            filename (str): database to open.
        Returns:
            bool: flag indicating success.
        """
        try:
            self._conn = connect(filename)
        except Error as error:
            print("Error: %s." % (" ".join(error.args)))
            return False

        return True

    def open(self, filename: str) -> bool:
        """open

        Opens a named database.

        Args:
            filename (str): database to open.

        Returns:
            bool: flag indicating success.
        """
        # print(f"SQLite_shell connecting to: {filename}.")

        #  Check file exists.

        if not path.exists(filename):
            print(f"Error: database '{filename}' does not exist..")
            return False

        if path.isdir(filename):
            print(f"Error: '{filename}' is a directory not a file..")
            return False

        #  Try to connect and report error if connection fails.

        try:
            self._conn = connect(f"file:{filename}?mode=rw", uri=True)
            self._conn.execute("PRAGMA schema_version;")
        except Error as error:
            print("Error: %s." % (" ".join(error.args)))
            return False

        #  If connection succeeds store the cursor.
        self._cur = self._conn.cursor()

        #  Some simple set up.

        self._conn.execute("PRAGMA foreign_keys = ON;")

        # print("SQLite_shell connected.")
        return True

    def close(self) -> bool:
        try:
            self._conn.close()
        except AttributeError:
            print("Error: not currently connected to an open database..")
            self._results = []
            return False

        return True

    def delete(self, filename: str) -> bool:
        #  Check file exists.

        if not path.exists(filename):
            print(f"Error: database '{filename}' does not exist..")
            return False

        if path.isdir(filename):
            print(f"Error: '{filename}' is a directory not a file..")
            return False

        #  Try to connect if that succeeds the file is a database so delete it.

        try:
            _conn = connect(f"file:{filename}?mode=rw", uri=True)
            _conn.execute("PRAGMA schema_version;")
            _conn.close()
        except Error as error:
            print("Error: %s." % (" ".join(error.args)))
            return False

        try:
            remove(filename)
        except PermissionError as error:
            print(f"Error: {error}.")
            return False

        return True

    def execute_sql(self, sql: str, echo: str) -> list[Any]:
        """execute_sql

        Executes a string as sql, passing parameters if available.

        Args:
            sql (str): sql to execute.
            parameters (list[dict[str, Any]]): parameters to pass to sql.
            echo (bool): flag indicating if sql should be echoed to console.

        Returns:
            list[Any]: results of executing sql.
        """

        #  Initialise variables.

        self._results: list[Any] = []

        #  If echo is on and string is not blank then echo sql to console.

        if echo == "ON" and sql.lower().strip() != "":
            print(f"{sql}")

        #  Try to execute string as sql, trapping various errors.
        #  If error occurs, print message and abort, returning an empty list as the result.

        if sql != "":
            try:
                with self._conn:
                    try:
                        if sql.count(";") > 1:
                            self._cur.executescript(sql)
                        else:
                            self._cur.execute(sql)
                            self._results = self._cur.fetchall()
                        if self._results == []:
                            print("** Empty result set **")
                    except IntegrityError as error:
                        print("Error: %s." % (" ".join(error.args)))
                        self._results = []
                    except OperationalError as error:
                        print("Error: %s." % (" ".join(error.args)))
                        self._results = []
                    except ProgrammingError as error:
                        print("Error: %s." % (" ".join(error.args)))
                        self._results = []
            except AttributeError as error:
                print(
                    f"Error: could not execute sql - {error}. Maybe database is not open.."
                )
                self._results = []

        return self._results
