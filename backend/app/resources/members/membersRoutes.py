from app.resources.members.auth import (
    RegisterResource,
    LoginResource,
    LogoutResource,
    MeResource,
    RefreshResource,
)
from app.resources.members.membersResources import (
    MembersListResource,
    MembersDetailResource,
)


def initialize_routes(api):
    # Auth
    api.add_resource(RegisterResource,    '/members/register')
    api.add_resource(LoginResource,       '/members/login')
    api.add_resource(LogoutResource,      '/members/logout')
    api.add_resource(MeResource,          '/members/me')
    api.add_resource(RefreshResource,     '/members/refresh')

    # CRUD
    api.add_resource(MembersListResource,   '/members')
    api.add_resource(MembersDetailResource, '/members/<int:member_id>')