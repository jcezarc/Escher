import sys
from backend_generator import BackendGenerator
from frontend_generator import FrontendGenerator

CURR_VERSION = '1.20.5.26.06.57'

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
    back = BackendGenerator(sys.argv[1])
    if back.json_info is None:
        return
    front = FrontendGenerator(sys.argv[1])
    print('--- Backend ---')
    back.exec()
    print('\n--- Frontend ---')
    front.exec()
    print('\nSuccess!')

main()
