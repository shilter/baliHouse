from app.resources.leads.leadsResources import LeadsListResource, LeadsDetailResource


def initialize_routes(api):
    api.add_resource(LeadsListResource, '/leads')
    api.add_resource(LeadsDetailResource, '/leads/<string:lead_id>')
