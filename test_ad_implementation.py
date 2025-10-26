#!/usr/bin/env python
#
# Simple test to verify AD authentication implementation
#

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

# Test that our AD module can be imported
try:
    from api.apps.auth.ad import ADClient
    print("✓ ADClient module imported successfully")
except ImportError as e:
    print(f"✗ Failed to import ADClient: {e}")
    sys.exit(1)

# Test that our AD service can be imported
try:
    from api.db.services.ad_service import ADGroupMappingService
    print("✓ ADGroupMappingService module imported successfully")
except ImportError as e:
    print(f"✗ Failed to import ADGroupMappingService: {e}")
    sys.exit(1)

# Test that AD client is registered in the auth system
try:
    from api.apps.auth import CLIENT_TYPES
    if 'ad' in CLIENT_TYPES:
        print("✓ AD client type registered successfully")
    else:
        print("✗ AD client type not found in CLIENT_TYPES")
        sys.exit(1)
except ImportError as e:
    print(f"✗ Failed to access CLIENT_TYPES: {e}")
    sys.exit(1)

# Test that the UserService has AD methods
try:
    from api.db.services.user_service import UserService
    if hasattr(UserService, 'create_or_update_ad_user'):
        print("✓ UserService has AD methods")
    else:
        print("✗ UserService missing AD methods")
        sys.exit(1)
except ImportError as e:
    print(f"✗ Failed to import UserService: {e}")
    sys.exit(1)

print("\n✓ All basic imports and registrations are working correctly")
print("\nAD Authentication Implementation Summary:")
print("- ADClient class created for AD authentication")
print("- AD configuration support added to settings")
print("- Group to tenant mapping service implemented")
print("- AD-specific user creation and management added")
print("- New /login/ad endpoint created")
print("- ldap3 dependency added to project")
print("\nThe implementation is ready for configuration and testing with a real AD server.")