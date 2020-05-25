from flask_restful import Resource
from service.%table%_service import %table%Service

class %table%ById(Resource):
    def get(self, %pk_field%):
        """
        Search in  %table% by the filed %pk_field%

        #Read
        """
        service = %table%Service()
        return service.find(None, %pk_field%)

    def delete(self, %pk_field%):
        """
        Delete a record of %table%

        #Write
        """
        service = %table%Service()
        return service.delete([%pk_field%])
