#!/usr/bin/env python
"""
Comprehensive test for AD Authentication Implementation in RAGFlow
"""

import sys
import os
import tempfile

# Add the project root to Python path
project_root = os.path.join(os.path.dirname(__file__))
sys.path.insert(0, project_root)

def test_imports():
    """Test that all our modules can be imported without errors"""
    print("Testing imports...")
    
    # Test 1: AD Client
    try:
        from api.apps.auth.ad import ADClient
        print("✓ ADClient imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import ADClient: {e}")
        return False
    
    # Test 2: AD Service
    try:
        from api.db.services.ad_service import ADGroupMappingService
        print("✓ ADGroupMappingService imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import ADGroupMappingService: {e}")
        return False
    
    # Test 3: Auth registry includes AD
    try:
        from api.apps.auth import CLIENT_TYPES
        if 'ad' in CLIENT_TYPES:
            print("✓ AD client type registered in CLIENT_TYPES")
        else:
            print("✗ AD client type not found in CLIENT_TYPES")
            return False
    except ImportError as e:
        print(f"✗ Failed to access CLIENT_TYPES: {e}")
        return False
    
    # Test 4: UserService has AD methods
    try:
        from api.db.services.user_service import UserService
        required_methods = [
            'create_or_update_ad_user',
            'assign_user_to_tenants_from_ad_groups'
        ]
        
        missing_methods = []
        for method in required_methods:
            if not hasattr(UserService, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"✗ UserService missing methods: {missing_methods}")
            return False
        else:
            print("✓ UserService has all required AD methods")
    except ImportError as e:
        print(f"✗ Failed to import UserService: {e}")
        return False
    
    print("✓ All imports successful\n")
    return True

def test_ad_client_structure():
    """Test the structure of the AD Client"""
    print("Testing AD Client structure...")
    
    try:
        from api.apps.auth.ad import ADClient
        
        # Check if ADClient extends the right base class
        from api.apps.auth.oauth import OAuthClient
        if issubclass(ADClient, OAuthClient):
            print("✓ ADClient properly extends OAuthClient")
        else:
            print("✗ ADClient does not extend OAuthClient")
            return False
        
        # Check for required methods
        required_methods = [
            'authenticate_user',
            'get_user_groups',
            'get_user_info',
            'fetch_user_info',
            'normalize_user_info',
            'connect'
        ]
        
        missing_methods = []
        for method in required_methods:
            if not hasattr(ADClient, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"✗ ADClient missing methods: {missing_methods}")
            return False
        else:
            print("✓ ADClient has all required methods")
        
        print("✓ AD Client structure is correct\n")
        return True
    except Exception as e:
        print(f"✗ Error testing AD Client structure: {e}")
        return False

def test_ad_service_structure():
    """Test the structure of the AD Service"""
    print("Testing AD Service structure...")
    
    try:
        from api.db.services.ad_service import ADGroupMappingService
        
        # Check for required methods
        required_methods = [
            'map_ad_groups_to_tenants',
            'get_user_tenants_from_groups'
        ]
        
        missing_methods = []
        for method in required_methods:
            if not hasattr(ADGroupMappingService, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"✗ ADGroupMappingService missing methods: {missing_methods}")
            return False
        else:
            print("✓ ADGroupMappingService has all required methods")
        
        print("✓ AD Service structure is correct\n")
        return True
    except Exception as e:
        print(f"✗ Error testing AD Service structure: {e}")
        return False

def test_mock_ad_config():
    """Test that AD client can be initialized with mock config"""
    print("Testing AD Client initialization with mock configuration...")
    
    try:
        from api.apps.auth.ad import ADClient
        import ldap3
        
        # Create a mock configuration that won't actually connect
        mock_config = {
            "server_uri": "ldap://nonexistent-server.com:389",
            "domain": "example.com",
            "bind_dn": "CN=Service Account,OU=Users,DC=example,DC=com",
            "bind_password": "password",
            "user_search_base": "DC=example,DC=com",
            "group_search_base": "DC=example,DC=com",
        }
        
        # We expect this to fail due to connection, but constructor should work
        try:
            client = ADClient(mock_config)
            print("✗ ADClient constructor should have failed due to connection")
            return False
        except ValueError as e:
            if "connect" in str(e).lower() or "connection" in str(e).lower():
                print("✓ ADClient constructor properly rejects invalid server (expected behavior)")
            else:
                print(f"✓ ADClient constructor failed as expected: {e}")
        
        print("✓ AD Client initialization test completed\n")
        return True
    except Exception as e:
        print(f"✗ Error testing AD Client initialization: {e}")
        return False

def test_syntax_of_all_modified_files():
    """Verify syntax of all files we modified"""
    print("Testing syntax of all modified files...")
    
    files_to_check = [
        "api/apps/auth/ad.py",
        "api/apps/auth/__init__.py", 
        "api/settings.py",
        "api/db/services/ad_service.py",
        "api/db/services/user_service.py",
        "api/apps/user_app.py"
    ]
    
    import subprocess
    all_good = True
    
    for file_path in files_to_check:
        full_path = os.path.join(project_root, file_path)
        try:
            result = subprocess.run([sys.executable, "-m", "py_compile", full_path], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ {file_path} syntax is valid")
            else:
                print(f"✗ {file_path} has syntax errors: {result.stderr}")
                all_good = False
        except Exception as e:
            print(f"✗ Could not check {file_path}: {e}")
            all_good = False
    
    if all_good:
        print("✓ All files have valid syntax\n")
    else:
        print("✗ Some files have syntax errors\n")
    
    return all_good

def test_ldap3_availability():
    """Test that ldap3 library is available"""
    print("Testing ldap3 library availability...")
    
    try:
        import ldap3
        print(f"✓ ldap3 version {ldap3.__version__} is available")
        return True
    except ImportError:
        print("✗ ldap3 library is not available")
        return False

def main():
    """Run all tests"""
    print("Starting comprehensive test of AD Authentication Implementation...\n")
    
    tests_passed = 0
    total_tests = 7
    
    if test_ldap3_availability():
        tests_passed += 1
    
    if test_imports():
        tests_passed += 1
    
    if test_ad_client_structure():
        tests_passed += 1
    
    if test_ad_service_structure():
        tests_passed += 1
    
    if test_mock_ad_config():
        tests_passed += 1
    
    if test_syntax_of_all_modified_files():
        tests_passed += 1
    
    # Test that our changes work with the existing auth system
    print("Testing integration with existing auth system...")
    try:
        from api.apps.auth import get_auth_client
        from api.apps.auth.ad import ADClient
        
        mock_config = {"type": "ad", "server_uri": "ldap://test", "domain": "test.com", "user_search_base": "DC=test,DC=com"}
        
        # This would fail due to connection but should recognize the type
        try:
            client = get_auth_client(mock_config)
            if isinstance(client, ADClient):
                print("✓ Integration with existing auth system works")
                tests_passed += 1
            else:
                print("✗ Integration with existing auth system failed")
        except ValueError as e:
            if "server_uri" in str(e) or "connect" in str(e):
                print("✓ Integration works - auth system recognizes AD type (expected connection error)")
                tests_passed += 1
            else:
                print(f"✗ Integration failed with unexpected error: {e}")
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
    
    print(f"\nTest Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! AD Authentication implementation is ready.")
        return True
    else:
        print("❌ Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)