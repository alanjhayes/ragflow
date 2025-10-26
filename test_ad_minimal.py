#!/usr/bin/env python
"""
Minimal test for AD Authentication Implementation in RAGFlow
This test focuses only on the syntax and structure of our implementation
without requiring full RAGFlow dependencies
"""

import sys
import os
import tempfile
import subprocess

# Add the project root to Python path
project_root = os.path.join(os.path.dirname(__file__))
sys.path.insert(0, project_root)

def test_syntax_of_all_modified_files():
    """Verify syntax of all files we modified"""
    print("Testing syntax of all modified files...")
    
    files_to_check = [
        "api/apps/auth/ad.py",
        "api/apps/auth/__init__.py", 
        "api/settings.py",
        "api/db/services/ad_service.py",
        "api/db/services/user_service.py",  # Only check syntax, not execution
        "api/apps/user_app.py"  # Only check syntax, not execution
    ]
    
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

def test_ad_client_structure():
    """Test the structure of the AD Client by examining the source code"""
    print("Testing AD Client structure...")
    
    try:
        # Check if the file exists and read it
        ad_client_path = os.path.join(project_root, "api/apps/auth/ad.py")
        with open(ad_client_path, 'r') as f:
            content = f.read()
        
        # Check for key components without importing
        required_components = [
            'class ADClient',
            'def authenticate_user',
            'def get_user_groups', 
            'def get_user_info',
            'ldap3',
            'sAMAccountName'
        ]
        
        missing_components = []
        for component in required_components:
            if component not in content:
                missing_components.append(component)
        
        if missing_components:
            print(f"✗ ADClient missing components: {missing_components}")
            return False
        else:
            print("✓ ADClient has all required components")
        
        print("✓ AD Client structure is correct\n")
        return True
    except Exception as e:
        print(f"✗ Error testing AD Client structure: {e}")
        return False

def test_auth_registry_update():
    """Test that the auth registry includes AD type"""
    print("Testing auth registry update...")
    
    try:
        auth_init_path = os.path.join(project_root, "api/apps/auth/__init__.py")
        with open(auth_init_path, 'r') as f:
            content = f.read()
        
        # Check if AD is registered
        if 'ad' in content and 'ADClient' in content:
            print("✓ AD client type is registered in auth registry")
        else:
            print("✗ AD client type is not properly registered in auth registry")
            return False
        
        print("✓ Auth registry is correctly updated\n")
        return True
    except Exception as e:
        print(f"✗ Error testing auth registry: {e}")
        return False

def test_settings_update():
    """Test that settings include AD config"""
    print("Testing settings update...")
    
    try:
        settings_path = os.path.join(project_root, "api/settings.py")
        with open(settings_path, 'r') as f:
            content = f.read()
        
        # Check if AD config is added
        if 'AD_CONFIG' in content:
            print("✓ AD_CONFIG is added to settings")
        else:
            print("✗ AD_CONFIG is not in settings")
            return False
        
        print("✓ Settings correctly updated\n")
        return True
    except Exception as e:
        print(f"✗ Error testing settings: {e}")
        return False

def test_user_app_update():
    """Test that user_app.py includes AD endpoint"""
    print("Testing user_app update...")
    
    try:
        user_app_path = os.path.join(project_root, "api/apps/user_app.py")
        with open(user_app_path, 'r') as f:
            content = f.read()
        
        # Check if AD login endpoint is added
        if 'ad_login' in content and '/login/ad' in content:
            print("✓ AD login endpoint is added to user_app")
        else:
            print("✗ AD login endpoint is not in user_app")
            return False
        
        print("✓ User app correctly updated\n")
        return True
    except Exception as e:
        print(f"✗ Error testing user_app: {e}")
        return False

def test_dependency_added():
    """Test that ldap3 dependency was added to pyproject.toml"""
    print("Testing dependency addition...")
    
    try:
        pyproject_path = os.path.join(project_root, "pyproject.toml")
        with open(pyproject_path, 'r') as f:
            content = f.read()
        
        # Check if ldap3 is in dependencies
        if 'ldap3' in content:
            print("✓ ldap3 dependency is added to pyproject.toml")
        else:
            print("✗ ldap3 dependency is not in pyproject.toml")
            return False
        
        print("✓ Dependency correctly added\n")
        return True
    except Exception as e:
        print(f"✗ Error testing dependency: {e}")
        return False

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
    print("Starting minimal test of AD Authentication Implementation...\n")
    
    tests_passed = 0
    total_tests = 7
    
    if test_ldap3_availability():
        tests_passed += 1
    
    if test_syntax_of_all_modified_files():
        tests_passed += 1
    
    if test_ad_client_structure():
        tests_passed += 1
    
    if test_auth_registry_update():
        tests_passed += 1
    
    if test_settings_update():
        tests_passed += 1
    
    if test_user_app_update():
        tests_passed += 1
    
    if test_dependency_added():
        tests_passed += 1
    
    print(f"\nTest Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! AD Authentication implementation is syntactically correct.")
        print("\nThe implementation includes:")
        print("- ADClient class with authentication methods")
        print("- Integration with existing auth system")
        print("- AD configuration support in settings")
        print("- AD login endpoint in user app")
        print("- ldap3 dependency in project file")
        print("- AD service for group mapping")
        return True
    else:
        print("❌ Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)