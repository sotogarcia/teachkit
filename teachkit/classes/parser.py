from argparse import ArgumentParser, ArgumentTypeError
from os import getcwd, path


class CommandLineInterface(object):

    _title = 'Teachkit: A tool for managing groups, resources, and students.'

    # -------------------------------------------------------------------------
    # Singleton
    # -------------------------------------------------------------------------

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    # -------------------------------------------------------------------------
    # Constructor
    # -------------------------------------------------------------------------

    def __init__(self):
        """
        Initialize the CommandLineInterface instance and configure the argument parser.
        """
        self.parser = argparse.ArgumentParser(description=self._title)

        self._configure_parser()
        self._args = self.parser.parse_args()

    # -------------------------------------------------------------------------
    # Configure parser
    # -------------------------------------------------------------------------

    def _configure_parser(self):
        """
        Set up the main parser and define subparsers for groups, students, and resources.
        """
        main_help = "Main commands"
        subparsers = self.parser.add_subparsers(
            dest="command", required=True, help=main_help
        )

        # Add parsers for each command group
        self._add_group_parser(subparsers)
        self._add_student_parser(subparsers)
        self._add_resource_parser(subparsers)

    def _add_group_parser(self, subparsers):
        """
        Define subcommands and arguments related to group management.

        Args:
            subparsers (argparse._SubParsersAction): The subparsers object from the main parser.
        """
        group_help = "Manage groups"
        parser = subparsers.add_parser("group", help=group_help)

        action_help = "Group actions"
        group_subparsers = parser.add_subparsers(
            dest="action", required=True, help=action_help
        )

        group_subparsers.add_parser("list", help="List all available groups")

        add_help = "Create a new group and its directory if it does not exist"
        add_parser = group_subparsers.add_parser("add", help=add_help)
        add_help = "Directory for the new group"
        add_parser.add_argument("directory", help=add_help, type=str)

        get_help = "Get a property value from the current group"
        get_parser = group_subparsers.add_parser("get", help=get_help)
        get_help = "Property to retrieve"
        get_parser.add_argument("property", help=get_help, type=str)

        set_help = "Set a property value for the current group"
        set_parser = group_subparsers.add_parser("set", help=set_help)
        set_help = "Property to set"
        set_parser.add_argument("property", help=set_help, type=str)
        set_help = "Value to assign to the property"
        set_parser.add_argument("value", help=set_help, type=str)

        del_help = "Delete an existing group and its directory"
        del_parser = group_subparsers.add_parser("del", help=del_help)
        del_help = "Directory of the group to delete"
        del_parser.add_argument("directory", help=del_help, type=str)

        print_help = "Print detailed information about the group"
        group_subparsers.add_parser("print", help=print_help)

    def _add_student_parser(self, subparsers):
        """
        Define subcommands and arguments related to student management.

        Args:
            subparsers (argparse._SubParsersAction): The subparsers object from the main parser.
        """
        student_help = "Manage students"
        parser = subparsers.add_parser("student", help=student_help)

        action_help = "Student actions"
        student_subparsers = parser.add_subparsers(
            dest="action", required=True, help=action_help
        )

        student_subparsers.add_parser(
            "list", help="List all students in the current group"
        )

        add_help = "Add a new student and its folder to the current group"
        add_parser = student_subparsers.add_parser("add", help=add_help)
        add_help = "Directory for the new student"
        add_parser.add_argument("directory", help=add_help, type=str)

        get_help = (
            "Retrieve a property of one or several students in the current group"
        )
        get_parser = student_subparsers.add_parser("get", help=get_help)
        get_help = "Property to retrieve"
        get_parser.add_argument("property", help=get_help, type=str)

        set_help = "Assign a property value for a student in the current group"
        set_parser = student_subparsers.add_parser("set", help=set_help)
        set_help = "Property to set"
        set_parser.add_argument("property", help=set_help, type=str)
        set_help = "Value to assign to the property"
        set_parser.add_argument("value", help=set_help, type=str)

        del_help = "Delete a student"
        del_parser = student_subparsers.add_parser("del", help=del_help)
        del_help = "Directory of the student to delete"
        del_parser.add_argument("directory", help=del_help, type=str)

        print_help = "Print student information"
        print_parser = student_subparsers.add_parser("print", help=print_help)
        print_help = "Directory of the student to print"
        print_parser.add_argument(
            "directory", nargs="?", help=print_help, type=str
        )

    def _add_resource_parser(self, subparsers):
        """
        Define subcommands and arguments related to resource management.

        Args:
            subparsers (argparse._SubParsersAction): The subparsers object from the main parser.
        """
        resource_help = "Manage resources"
        parser = subparsers.add_parser("resource", help=resource_help)

        action_help = "Resource actions"
        resource_subparsers = parser.add_subparsers(
            dest="action", required=True, help=action_help
        )

        list_help = "List resources"
        list_parser = resource_subparsers.add_parser("list", help=list_help)
        list_help = "Topic of the resources"
        list_parser.add_argument("topic", nargs="?", help=list_help, type=str)
        list_help = "Category within the topic"
        list_parser.add_argument("category", nargs="?", help=list_help, type=str)

        add_help = "Add resources"
        add_parser = resource_subparsers.add_parser("add", help=add_help)
        add_help = "Topic of the resource"
        add_parser.add_argument("topic", nargs="?", help=add_help, type=str)
        add_help = "Category within the topic"
        add_parser.add_argument("category", nargs="?", help=add_help, type=str)
        add_help = "Specific exercise"
        add_parser.add_argument("exercise", nargs="?", help=add_help, type=str)

        get_help = "Get resources"
        get_parser = resource_subparsers.add_parser("get", help=get_help)
        get_help = "Topic of the resource"
        get_parser.add_argument("topic", nargs="?", help=get_help, type=str)
        get_help = "Category within the topic"
        get_parser.add_argument("category", nargs="?", help=get_help, type=str)
        get_help = "Specific exercise"
        get_parser.add_argument("exercise", nargs="?", help=get_help, type=str)

        set_help = "Set resource properties"
        set_parser = resource_subparsers.add_parser("set", help=set_help)
        set_help = "Topic of the resource"
        set_parser.add_argument("topic", nargs="?", help=set_help, type=str)
        set_help = "Category within the topic"
        set_parser.add_argument("category", nargs="?", help=set_help, type=str)
        set_help = "Specific exercise"
        set_parser.add_argument("exercise", nargs="?", help=set_help, type=str)

        del_help = "Delete a resource"
        del_parser = resource_subparsers.add_parser("del", help=del_help)
        del_help = "Exercise to delete"
        del_parser.add_argument("exercise", help=del_help, type=str)

        print_help = "Print resource information"
        print_parser = resource_subparsers.add_parser("print", help=print_help)
        print_help = "Directory of the resource to print"
        print_parser.add_argument(
            "directory", nargs="?", help=print_help, type=str
        )

    # -------------------------------------------------------------------------
    # Access to the argument values
    # -------------------------------------------------------------------------

    def get(self, name, default=None, raise_if_missing=False):
        """
        Retrieve a specific argument from the parsed arguments.

        Args:
            name (str): The name of the argument to retrieve.
            default (any): The value to return if the argument is not found.
            raise_if_missing (bool): Raise AttributeError if argument is missing.

        Returns:
            any: The value of the requested argument or the default value.

        Raises:
            AttributeError: If raise_if_missing is True and the argument does not exist.

        Example:
            To retrieve the 'command' argument:
            >>> cli.get_arg("command")
        """
        if raise_if_missing and not hasattr(self._args, name):
            raise AttributeError(f"Argument '{name}' does not exist.")
        return getattr(self._args, name, default)

    def exists(self, name):
        return hasattr(self._args, name )
