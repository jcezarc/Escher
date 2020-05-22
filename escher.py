import sys
from backend_generator import BackendGenerator
from frontend_generator import FrontendGenerator

CURR_VERSION = '1.0'

def main():
    if len(sys.argv) < 2:
        print("""
            *** Escher {} ***

            How to use:
            > python Escher.py <JSON file>

            Example:
            > python Escher.py Movies
            """.format(
                CURR_VERSION
            )
        )
        return
    back = BackendGenerator(sys.argv[1])
    if back.json_info is None:
        return
    front = FrontendGenerator(sys.argv[1])
    print('--- Backend ---')
    back.exec()
    print('--- Frontend ---')
    front.exec()
    print('Success!')

main()
