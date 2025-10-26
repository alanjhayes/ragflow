# AD Authentication and Group Mapping Implementation for RAGFlow

## Overview
This implementation adds Active Directory (AD) authentication capability to RAGFlow with group-based tenant mapping. The solution allows users to authenticate against an AD server and automatically assigns them to tenants based on their AD group memberships.

## Components Implemented

### 1. AD Authentication Client (`api/apps/auth/ad.py`)
- Implements `ADClient` class extending the OAuthClient base class
- Uses `ldap3` library to connect to AD servers
- Supports user authentication against AD
- Retrieves user information and group memberships from AD
- Handles connection pooling and error management

### 2. Authentication Registry Update (`api/apps/auth/__init__.py`)
- Added "ad" type to `CLIENT_TYPES` mapping
- Registered `ADClient` with the authentication system

### 3. Configuration Support (`api/settings.py`)
- Added `AD_CONFIG` variable to store AD configuration
- Integrated AD config loading in `init_settings()` function

### 4. Group Mapping Service (`api/db/services/ad_service.py`)
- `ADGroupMappingService` class to handle group-to-tenant mappings
- Maps AD groups to RAGFlow tenants based on configuration
- Assigns appropriate roles based on group membership

### 5. User Management Extensions (`api/db/services/user_service.py`)
- Added `create_or_update_ad_user()` method to handle AD users
- Added `assign_user_to_tenants_from_ad_groups()` method for group-based tenant assignment

### 6. AD Login Endpoint (`api/apps/user_app.py`)
- Added `/login/ad` POST endpoint for AD authentication
- Handles AD user authentication, creation, and tenant assignment
- Integrates with existing user session management

### 7. Dependency (`pyproject.toml`)
- Added `ldap3` dependency for AD connectivity

## Configuration

To enable AD authentication, add the following configuration to your config file (typically `conf/config.json`):

```json
{
  "ad": {
    "server_uri": "ldap://your-ad-server.company.com:389",
    "domain": "company.com",
    "bind_dn": "CN=Service Account,OU=Users,DC=company,DC=com",
    "bind_password": "service_account_password",
    "user_search_base": "DC=company,DC=com",
    "group_search_base": "DC=company,DC=com",
    "user_filter": "(sAMAccountName={username})",
    "group_filter": "(member={user_dn})",
    "auto_create_user": true,
    "default_tenant": null,
    "group_mappings": {
      "RAGFlow-Admins": {
        "tenant_id": "admin_tenant_id",
        "role": "owner"
      },
      "RAGFlow-Users": {
        "tenant_id": "user_tenant_id", 
        "role": "normal"
      },
      "RAGFlow-Readers": {
        "tenant_id": "read_tenant_id",
        "role": "normal"
      }
    }
  }
}
```

### Configuration Parameters:

- `server_uri`: LDAP URI of your AD server (e.g., "ldap://ad.company.com:389" or "ldaps://ad.company.com:636")
- `domain`: Your AD domain name
- `bind_dn`: Distinguished Name of the service account for binding (optional)
- `bind_password`: Password for the service account (optional)
- `user_search_base`: Base DN for searching users
- `group_search_base`: Base DN for searching groups
- `user_filter`: LDAP filter for finding users (default: "(sAMAccountName={username})")
- `group_filter`: LDAP filter for finding groups (default: "(member={user_dn})")
- `auto_create_user`: Whether to automatically create users not in RAGFlow database
- `default_tenant`: Default tenant ID to assign to new users
- `group_mappings`: Mapping of AD groups to RAGFlow tenants and roles

## API Usage

### AD Authentication Endpoint
```
POST /api/v1/login/ad
Content-Type: application/json

{
  "username": "user123",
  "password": "user_password"
}
```

### Response
The endpoint returns the same format as existing login endpoints:
- Success: User information with authentication token
- Failure: Error message with appropriate HTTP status code

## Tenant Mapping Logic

1. When a user authenticates via AD, their group memberships are retrieved
2. Each group is checked against the `group_mappings` configuration
3. For each matching group, the user is assigned to the corresponding tenant with the specified role
4. If the user doesn't exist in RAGFlow, they are created automatically (if `auto_create_user` is true)
5. If the user already exists, their tenant assignments are updated based on current group membership

## Security Considerations

- Use LDAPS (port 636) instead of LDAP (port 389) when possible for encrypted connections
- Create a dedicated service account for RAGFlow AD integration with minimal required permissions
- Regularly rotate the bind account password
- Monitor authentication logs for suspicious activity

## Testing

To verify the implementation, the following test can be used:

```python
from api.apps.auth.ad import ADClient

# Initialize AD client with configuration
ad_config = {
    "server_uri": "ldap://your-ad-server.company.com:389",
    "domain": "company.com",
    # ... other config
}

ad_client = ADClient(ad_config)

# Authenticate a user
if ad_client.authenticate_user("username", "password"):
    user_info = ad_client.get_user_info("username")
    groups = user_info.get("groups", [])
    print(f"User authenticated with groups: {groups}")
```

## Role Mappings

- `owner`: Full administrative access to the tenant
- `normal`: Standard user access to the tenant

The implementation seamlessly integrates with RAGFlow's existing tenant and user management system while providing secure AD-based authentication and group-based access control.