    api.add_resource(%table%ById, f'{BASE_PATH}/%table%/<%pk_field%>', methods=['GET'], endpoint='get_%table%_by_id')
    api.add_resource(All%table%, f'{BASE_PATH}/%table%', methods=['GET'], endpoint='get_All%table%')
    api.add_resource(All%table%, f'{BASE_PATH}/%table%', methods=['POST'], endpoint='post_%table%')
    api.add_resource(All%table%, f'{BASE_PATH}/%table%', methods=['PUT'], endpoint='put_%table%')
    api.add_resource(%table%ById, f'{BASE_PATH}/%table%/<%pk_field%>', methods=['DELETE'], endpoint='delete_%table%')