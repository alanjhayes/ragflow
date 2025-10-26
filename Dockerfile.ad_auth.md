# Docker Configuration for AD Authentication

## Required Changes

To run RAGFlow with AD authentication in Docker, the following changes have been made:

### 1. System Dependencies (Dockerfile)
- Added `libsasl2-dev` and `libldap2-dev` packages required by ldap3

### 2. Python Dependencies (pyproject.toml)
- Added `ldap3>=2.9.1` dependency
- Updated `uv.lock` file with dependency information

## Building the Docker Image

To build the updated image with AD authentication support:

```bash
# Build the image
docker build -t ragflow:ad-auth .

# Or with your specific tag
docker build -t your-registry/ragflow:ad-auth .
```

## Configuration

To enable AD authentication, add the AD configuration to your RAGFlow config:

```yaml
ad:
  server_uri: "ldaps://your-ad-server.company.com:636"
  domain: "company.com"
  bind_dn: "CN=ragflow-service,OU=Service Accounts,DC=company,DC=com"
  bind_password: "service_account_password"
  user_search_base: "DC=company,DC=com"
  group_search_base: "DC=company,DC=com"
  user_filter: "(sAMAccountName={username})"
  group_filter: "(member={user_dn})"
  auto_create_user: true
  group_mappings:
    "RAGFlow-Admins":
      tenant_id: "admin_tenant_id"
      role: "owner"
    "RAGFlow-Users":
      tenant_id: "user_tenant_id"
      role: "normal"
```

## AD Authentication Endpoint

After deployment, the AD authentication endpoint will be available:
- `POST /api/v1/login/ad`

Request body:
```json
{
  "username": "ad_username",
  "password": "ad_password"
}
```

## Security Best Practices

1. Use LDAPS (port 636) instead of LDAP (port 389) for encrypted connections
2. Create a dedicated service account for RAGFlow AD integration with minimal required permissions
3. Store sensitive configuration values (like bind_password) in environment variables
4. Regularly rotate the bind account password

## Testing the Docker Image

To test the AD authentication in the Docker container:

1. Build the image with the changes
2. Run the container with proper AD configuration
3. Test the authentication endpoint: `POST /api/v1/login/ad`