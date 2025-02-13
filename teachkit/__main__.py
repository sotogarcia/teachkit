from classes.parser import CommandLineInterface
from classes.group import Group
from classes.student import Student
from sys import argv


def main():
    cmd = CommandLineInterface()
    init_args = cmd.args_dict

    target_class = cmd.target.title()

    try:
        target = globals()[target_class]()
        action = getattr(target, cmd.action)
        action()
    except Exception as ex:
        cmd = ' '.join(argv)
        print(f'The execution ended unsatisfactorily.\n{ex}.')


main()
