    elif id_route == '%table%':
        if not params:
            resource = All%table%
        else:
            resource = %table%ById
        model = %table%Model()
