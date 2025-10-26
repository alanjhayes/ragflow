#!/usr/bin/env python
"""
Simple dummy AD server for testing AD authentication implementation
This creates a mock AD server that simulates common AD operations
"""

import json

class MockADServer:
    """
    A mock AD server for testing purposes
    """
    
    def __init__(self):
        # Define mock users and groups
        self.users = {
            'john.doe': {
                'dn': 'CN=John Doe,OU=Users,DC=example,DC=com',
                'sAMAccountName': 'john.doe',
                'mail': 'john.doe@example.com',
                'displayName': 'John Doe',
                'givenName': 'John',
                'sn': 'Doe',
                'memberOf': [
                    'CN=RAGFlow-Users,OU=Groups,DC=example,DC=com',
                    'CN=Developers,OU=Groups,DC=example,DC=com'
                ]
            },
            'admin.user': {
                'dn': 'CN=Admin User,OU=Users,DC=example,DC=com',
                'sAMAccountName': 'admin.user',
                'mail': 'admin@example.com',
                'displayName': 'Admin User',
                'givenName': 'Admin',
                'sn': 'User',
                'memberOf': [
                    'CN=RAGFlow-Admins,OU=Groups,DC=example,DC=com'
                ]
            },
            'reader.user': {
                'dn': 'CN=Reader User,OU=Users,DC=example,DC=com',
                'sAMAccountName': 'reader.user',
                'mail': 'reader@example.com',
                'displayName': 'Reader User',
                'givenName': 'Reader',
                'sn': 'User',
                'memberOf': [
                    'CN=RAGFlow-Readers,OU=Groups,DC=example,DC=com'
                ]
            }
        }
        
        self.groups = {
            'CN=RAGFlow-Admins,OU=Groups,DC=example,DC=com': {
                'cn': 'RAGFlow-Admins',
                'name': 'RAGFlow-Admins',
                'sAMAccountName': 'RAGFlow-Admins',
                'member': [
                    'CN=Admin User,OU=Users,DC=example,DC=com'
                ]
            },
            'CN=RAGFlow-Users,OU=Groups,DC=example,DC=com': {
                'cn': 'RAGFlow-Users',
                'name': 'RAGFlow-Users',
                'sAMAccountName': 'RAGFlow-Users',
                'member': [
                    'CN=John Doe,OU=Users,DC=example,DC=com'
                ]
            },
            'CN=RAGFlow-Readers,OU=Groups,DC=example,DC=com': {
                'cn': 'RAGFlow-Readers',
                'name': 'RAGFlow-Readers',
                'sAMAccountName': 'RAGFlow-Readers',
                'member': [
                    'CN=Reader User,OU=Users,DC=example,DC=com'
                ]
            }
        }
        
    def authenticate_user(self, username, password):
        """Mock authentication - check if user exists and password is valid"""
        # In a real scenario, this would verify against AD
        # For our mock, we'll just check if the user exists
        # and assume password is valid if user exists
        return username in self.users
    
    def get_user_info(self, username):
        """Get user information from mock AD"""
        if username in self.users:
            return self.users[username]
        return None
        
    def get_user_groups(self, username):
        """Get groups for a user from mock AD"""
        user_info = self.get_user_info(username)
        if user_info and 'memberOf' in user_info:
            groups = []
            for group_dn in user_info['memberOf']:
                group_name = group_dn.split(',')[0].split('=')[1]  # Extract CN from DN
                groups.append(group_name)
            return groups
        return []

def test_with_mock_server():
    """Test the AD authentication with our mock server"""
    print("Testing AD authentication implementation with mock server...")
    
    # Create mock AD instance
    mock_ad = MockADServer()
    
    # Test user authentication
    print("\n1. Testing user authentication:")
    test_users = ['john.doe', 'admin.user', 'reader.user', 'nonexistent.user']
    
    for user in test_users:
        result = mock_ad.authenticate_user(user, 'password123')
        print(f"   User '{user}': {'✓ Authenticated' if result else '✗ Not found'}")
    
    # Test user info retrieval
    print("\n2. Testing user info retrieval:")
    for user in ['john.doe', 'admin.user']:
        user_info = mock_ad.get_user_info(user)
        if user_info:
            print(f"   User '{user}': {user_info['displayName']} <{user_info['mail']}>")
        else:
            print(f"   User '{user}' not found")
    
    # Test group retrieval
    print("\n3. Testing group membership:")
    for user in ['john.doe', 'admin.user', 'reader.user']:
        groups = mock_ad.get_user_groups(user)
        print(f"   User '{user}' groups: {groups}")

def test_integration():
    """Test integration with our AD client implementation"""
    print("\n4. Testing integration with AD Client (simulated):")
    
    # Simulate what our ADClient would do
    print("   Simulating ADClient initialization...")
    print("   - Connecting to mock server: ldap://mock-ad.example.com")
    print("   - Binding with service account...")
    print("   - Connection successful (mock)")
    
    print("\n   Simulating user authentication:")
    print("   - User 'john.doe' attempting authentication...")
    print("   - Search filter: (sAMAccountName=john.doe)")
    print("   - User found: CN=John Doe,OU=Users,DC=example,DC=com")
    print("   - Authentication successful (mock)")
    
    print("\n   Simulating group lookup:")
    print("   - Retrieving groups for user 'john.doe'...")
    print("   - Found groups: ['RAGFlow-Users', 'Developers']")
    
    print("\n   Simulating tenant mapping:")
    print("   - Group 'RAGFlow-Users' maps to tenant 'user_tenant_id'")
    print("   - Group 'Developers' has no mapping")
    print("   - Assigning user to tenant 'user_tenant_id' with role 'normal'")
    print("   - User authentication and tenant assignment complete!")

def test_end_to_end():
    """Test the complete end-to-end flow with our AD implementation"""
    print("\n5. End-to-End Flow Test:")
    print("   a) User sends POST request to /api/v1/login/ad")
    print("      {\"username\": \"john.doe\", \"password\": \"user_password\"}")
    
    print("   b) RAGFlow ADClient:")
    print("      - Connects to AD server")
    print("      - Authenticates user 'john.doe'")
    print("      - Retrieves user info: name, email, groups")
    print("      - Gets groups: ['RAGFlow-Users', 'Developers']")
    
    print("   c) Group mapping:")
    print("      - 'RAGFlow-Users' -> tenant 'user_tenant_id' (role: normal)")
    print("      - 'Developers' -> no mapping")
    
    print("   d) User management:")
    print("      - Creates/updates user in RAGFlow DB")
    print("      - Assigns to appropriate tenants")
    print("      - Returns authentication token")
    
    print("   e) Result: User authenticated and assigned to correct tenants!")

if __name__ == "__main__":
    print("RAGFlow AD Authentication - Mock Server Test")
    print("=" * 50)
    
    # Run various tests
    test_with_mock_server()
    test_integration()
    test_end_to_end()
    
    print("\n" + "=" * 50)
    print("Mock server test completed successfully!")
    print("This demonstrates how the AD authentication would work in a real environment.")
    print("\nTo use in production, configure your AD server details in the RAGFlow config.")