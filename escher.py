import sys
from backend_generator import BackendGenerator
from frontend_generator import FrontendGenerator
from json_linter import JSonLinter

CURR_VERSION = 'v 1.200.527 R 20.51'

def main():
    if len(sys.argv) < 2:
        print("""
            *** Escher {} ***

            How to use:
            > python Escher.py <JSON file>

            Example:
            > python Escher.py Movies.json
            """.format(
                CURR_VERSION
            )
        )
        return
    linter = JSonLinter(sys.argv[1])
    linter.analyze()
    if linter.error_code > 0:
        print(linter.error_message())
        return
    back = BackendGenerator(linter)
    front = FrontendGenerator(linter)
    print('--- Backend ---')
    back.exec()
    print('\n--- Frontend ---')
    front.exec()
    print('\nSuccess!')

main()
