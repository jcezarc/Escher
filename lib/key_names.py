JSON_KEYS = [
    'table',
    'pk_field',
    'field_list',
    'nested',
]
ANGULAR_KEYS = [
    'title',
    'image',
    'detail',
    'label'
]

JSON_SAMPLE = {
    "tables": [
        {
            "table": "TableONE",
            "pk_field": "field01",
            "field_list": {
                "field01": "str",
                "field02": "float"
            },
            "Angular": {
                "title": "field01",
                "detail": "field02"
            }
        },
        {
            "table": "TableTWO",
            "pk_field": "field01",
            "field_list": {
                "field01": "int",
                "field02": "date",
                "field03": "str",
                "field04": "str",
                "field05": "str"
            },
            "nested": {
                "one": "TableONE"
            },
            "Angular": {
                "title": "field02",
                "detail": "field03",
                "label": "field04",
                "label-colors": {
                    "blue": "type01",
                    "green": "type02",
                    "yellow": "type03",
                    "red": "type04",
                },
                "image": "field05"
            }
        }
    ]
}