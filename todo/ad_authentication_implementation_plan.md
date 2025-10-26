# AD Authentication and Group Mapping Implementation Plan for RAGFlow

## Current State Analysis
1. RAGFlow has a flexible OAuth/OIDC authentication system with plugin architecture in `/api/apps/auth/`
2. Uses "tenants" as organizational units (similar to namespaces)
3. Has UserTenant model allowing users to belong to multiple tenants with different roles
4. No existing AD/LDAP authentication support

## Implementation Plan

### Phase 1: AD Authentication Integration
1. **Create AD Authentication Provider** (`api/apps/auth/ad.py`):
   - Implement ADClient class extending OAuthClient
   - Use python-ldap3 for AD connectivity
   - Support user authentication and group membership lookup
   - Include configuration for server URI, domain, search bases

2. **Update Authentication Registry** (`api/apps/auth/__init__.py`):
   - Add 'ad' type to CLIENT_TYPES
   - Register ADClient with the authentication system

3. **Add AD Configuration Support** (`api/settings.py`):
   - Update configuration loading to support AD settings
   - Add environment variables for AD configuration

### Phase 2: Group to Tenant Mapping
1. **Extend User Model**:
   - Add AD group mapping functionality
   - Store group memberships in session/context

2. **Create Group Mapping Configuration**:
   - Map AD groups to RAGFlow tenants
   - Define roles within tenants based on AD groups

3. **Update Tenant Access Logic**:
   - Modify tenant access control to consider AD group membership
   - Implement group-based tenant assignment during login

### Phase 3: Implementation Details
1. **New endpoints**:
   - `/login/ad` for AD authentication
   - Update existing login to support AD

2. **Database changes** (if needed):
   - Add tables for storing AD group mappings
   - User-AD-group relationships

3. **Configuration examples**:
   - Sample configuration for AD integration
   - Group mapping examples

## Required Dependencies
- `ldap3` - for AD connectivity
- `python-ldap` - alternative AD library (if needed)

## Files to Modify
1. `api/apps/auth/__init__.py` - Register AD client
2. `api/apps/auth/ad.py` - New AD authentication implementation
3. `api/apps/user_app.py` - Add AD login endpoints
4. `api/settings.py` - Add AD configuration support
5. `api/db/db_models.py` - Potentially extend models for group mapping
6. `api/db/services/user_service.py` - Update user management for AD users

## Implementation Prompt
"When implementing AD authentication in RAGFlow, create an ADClient that extends the OAuthClient, connects to AD servers using ldap3, authenticates users, retrieves group memberships, and maps AD groups to RAGFlow tenants. The system should allow configuration of AD server settings, group-to-tenant mappings, and integrate with the existing user management system."