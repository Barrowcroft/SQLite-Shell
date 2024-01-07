CONFIG_FILENAME = "configuration.txt"

INFO = "Simple SQLite Shell. v.1.0.0 - Barrowcroft, Dec 2023"

HELP_TEXT = (
    INFO
    + """
    
This is a very simple SQLite shell.

To execute an sql statement enter the statement on one or more lines, the final line ending with a semi-colon.
Once the statement has been entered it will be executed, and the results returned. Alternatively, execute a saved
script using the .script command.

There are a number of built-in commands:

    .create     creates a database - provide name of database.
    .open       opens a database - provide name of database, or '?'.
    .close      closes the current database.
    .delete     deletes a database - provide name of database.

    .schema     shows the database schema.
    .tables     lists tables in database.
    .describe   describes a named table - provide name of table.

    .cwd        sets the current working directory  - provide path of directory, or '?'.
    .dir        lists files in the current working directory.

    .echo       turns on/off echoing of sql when executing script - provide 'on' or 'off', or '?'. Default 'off'.
    .edit       starts the system editor.
    .script     executes a script - provide name of script, or '?'.
    .width      sets the width of the pretty-printed output - provide width,  or '?'. Default = 80.

    .exit       exits the shell.
    .help       shows this information."""
)
