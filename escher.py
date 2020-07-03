import sys
from lib.backend_generator import BackendGenerator
from lib.frontend_generator import FrontendGenerator
from lib.json_linter import JSonLinter
from lib.argument_parser import ArgumentParser
from lib.version import CURR_VERSION

def main():
    if len(sys.argv) < 2:
        print("""
            *** Escher {} ***

            How to use:
            > python Escher.py <JSON file>

            Example:
            > python Escher.py Movies.json

            * for more help, use --help
            """.format(
                CURR_VERSION
            )
        )
        return
    parser = ArgumentParser(sys.argv)
    if parser.funcs:
        parser.exec_funcs()
        return
    linter = JSonLinter(parser.file_name, parser.frontend)
    linter.analyze()
    if linter.error_code > 0:
        print(linter.error_message())
        return
    if parser.backend:
        back = BackendGenerator(linter)
        print('--- Backend ---')
        back.run()
    if parser.frontend:
        front = FrontendGenerator(linter)
        print('\n--- Frontend ---')
        front.run()
    print('\nSuccess!')

main()
