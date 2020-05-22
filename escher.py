import sys
from backend_generator import BackendGenerator
from frontend_generator import FrontendGenerator


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
    front = FrontendGenerator(sys.argv[1])
    print('--- Backend ---')
    back.exec()
    print('--- Frontend ---')
    front.exec()
    print('Success!')
