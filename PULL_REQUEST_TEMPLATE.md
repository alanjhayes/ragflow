# AD Authentication and Group Mapping Implementation

## Summary
This PR implements Active Directory (AD) authentication with group-to-tenant mapping functionality for RAGFlow. Users can now authenticate using their AD credentials and are automatically assigned to appropriate tenants based on their AD group memberships.

## Features Implemented

### 1. AD Authentication System
- Added `ADClient` class that extends the existing OAuthClient architecture
- Implemented AD authentication using the `ldap3` library
- Supports user authentication, information retrieval, and group membership lookup
- Includes proper error handling and logging

### 2. Group-to-Tenant Mapping
- Created `ADGroupMappingService` to handle mapping of AD groups to RAGFlow tenants
- Supports role assignment based on AD group membership (owner/normal roles)
- Configurable group mappings via configuration

### 3. API Integration
- Added new endpoint: `POST /api/v1/login/ad`
- Supports the same authentication flow and response format as existing login endpoints
- Maintains compatibility with existing user session management

### 4. User Management
- Added methods to create/update AD users in RAGFlow
- Implements automatic tenant assignment based on group membership
- Preserves existing user management patterns

## Files Changed

### New Files:
- `api/apps/auth/ad.py` - AD Authentication Client implementation
- `api/db/services/ad_service.py` - AD Group Mapping Service

### Modified Files:
- `api/apps/auth/__init__.py` - Added AD client registration
- `api/settings.py` - Added AD configuration support
- `api/db/services/user_service.py` - Added AD user management methods
- `api/apps/user_app.py` - Added AD login endpoint
- `pyproject.toml` - Added ldap3 dependency

## Configuration

To enable AD authentication, add the following configuration:

```json
{
  "ad": {
    "server_uri": "ldaps://your-ad-server.company.com:636",
    "domain": "company.com",
    "bind_dn": "CN=ragflow-service,OU=Service Accounts,DC=company,DC=com",
    "bind_password": "service_account_password",
    "user_search_base": "DC=company,DC=com",
    "group_search_base": "DC=company,DC=com",
    "user_filter": "(sAMAccountName={username})",
    "group_filter": "(member={user_dn})",
    "auto_create_user": true,
    "group_mappings": {
      "RAGFlow-Admins": {
        "tenant_id": "admin_tenant_id",
        "role": "owner"
      },
      "RAGFlow-Users": {
        "tenant_id": "user_tenant_id",
        "role": "normal"
      }
    }
  }
}
```

## Testing
- All implementation files pass Python syntax validation
- Mock server testing confirms proper functionality
- Integration with existing auth system verified
- End-to-end authentication flow tested

## Breaking Changes
- No breaking changes to existing functionality
- All existing authentication methods continue to work
- New functionality is opt-in via configuration

## Dependencies Added
- `ldap3` - for AD/LDAP connectivity

## Security Considerations
- Supports both LDAP and LDAPS connections
- Uses service accounts for AD binding (should be properly secured)
- Maintains existing RAGFlow security model
- Preserves user session management

## Usage
Users can authenticate via:
```bash
curl -X POST http://your-ragflow/api/v1/login/ad \
     -H "Content-Type: application/json" \
     -d '{"username": "ad_username", "password": "ad_password"}'
```

The system will authenticate against AD, retrieve group memberships, map groups to tenants based on configuration, and create appropriate user-tenant relationships.