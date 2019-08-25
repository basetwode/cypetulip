
# Baseline configuration.
from django_auth_ldap.config import LDAPSearch
from utils.ldap import Ldap

ldap = Ldap.objects.all()
AUTH_LDAP_SERVER_URI = ldap.server_uri

AUTH_LDAP_BIND_DN = ldap.bind_dn
AUTH_LDAP_BIND_PASSWORD = ldap.bind_password
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    ldap.user_search, ldap.SCOPE_SUBTREE, "(uid=%(user)s)"
)
# Or:
# AUTH_LDAP_USER_DN_TEMPLATE = 'uid=%(user)s,ou=users,dc=example,dc=com'

# Set up the basic group parameters.
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    ldap.group_search,
    ldap.SCOPE_SUBTREE,
    "(objectClass=groupOfNames)",
)
AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr="cn")

# Simple group restrictions
AUTH_LDAP_REQUIRE_GROUP = ldap.group_require
AUTH_LDAP_DENY_GROUP = ldap.group_deny

# Populate the Django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = ldap.user_attr_map

AUTH_LDAP_USER_FLAGS_BY_GROUP = ldap.user_flag_by_groups

# This is the default, but I like to be explicit.
AUTH_LDAP_ALWAYS_UPDATE_USER = True

# Use LDAP group membership to calculate group permissions.
AUTH_LDAP_FIND_GROUP_PERMS = True

# Cache distinguished names and group memberships for an hour to minimize
# LDAP traffic.
AUTH_LDAP_CACHE_TIMEOUT = 3600

# Keep ModelBackend around for per-user permissions and maybe a local
# superuser.
AUTHENTICATION_BACKENDS = (
    "django_auth_ldap.backend.LDAPBackend",
    "django.contrib.auth.backends.ModelBackend",
)
