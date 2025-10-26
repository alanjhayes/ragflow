#
#  Copyright 2025 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import logging
from api.db.services.user_service import UserTenantService, TenantService
from api.db.db_models import User, Tenant, UserTenant
from api.utils import get_uuid
from api.db import UserTenantRole, StatusEnum


class ADGroupMappingService:
    """
    Service to handle mapping of AD groups to RAGFlow tenants and roles.
    """
    
    @classmethod
    def map_ad_groups_to_tenants(cls, user_id: str, ad_groups: list):
        """
        Map AD groups to tenants for the given user.
        
        Args:
            user_id: The ID of the user
            ad_groups: List of AD group names the user belongs to
        """
        try:
            # Find all tenants that have group mappings
            # For each group the user belongs to, map to the corresponding tenant
            from api.settings import AD_CONFIG
            
            ad_group_mappings = AD_CONFIG.get("group_mappings", {})
            
            for group_name in ad_groups:
                # Check if this group has a mapping
                if group_name in ad_group_mappings:
                    tenant_id = ad_group_mappings[group_name]
                    
                    # Check if the tenant exists
                    tenant = TenantService.query(id=tenant_id)
                    if not tenant:
                        logging.warning(f"Tenant {tenant_id} does not exist for AD group {group_name}")
                        continue
                    
                    # Check if the user is already assigned to this tenant
                    existing_assignment = UserTenantService.query(user_id=user_id, tenant_id=tenant_id)
                    if existing_assignment:
                        # Update the role if needed
                        role = ad_group_mappings[group_name].get("role", UserTenantRole.NORMAL.value)
                        UserTenantService.update_by_id(
                            existing_assignment[0].id,
                            {"role": role}
                        )
                    else:
                        # Create new user-tenant assignment
                        user_tenant = {
                            "id": get_uuid(),
                            "user_id": user_id,
                            "tenant_id": tenant_id,
                            "role": ad_group_mappings[group_name].get("role", UserTenantRole.NORMAL.value),
                            "invited_by": user_id,
                            "status": StatusEnum.VALID.value
                        }
                        UserTenantService.insert(**user_tenant)
                        
                    logging.info(f"Assigned user {user_id} to tenant {tenant_id} based on AD group {group_name}")
        
        except Exception as e:
            logging.error(f"Error mapping AD groups to tenants: {e}")
    
    @classmethod
    def get_user_tenants_from_groups(cls, ad_groups: list):
        """
        Get all tenants associated with the user's AD groups.
        
        Args:
            ad_groups: List of AD group names the user belongs to
            
        Returns:
            List of tenant IDs associated with the AD groups
        """
        from api.settings import AD_CONFIG
        
        ad_group_mappings = AD_CONFIG.get("group_mappings", {})
        tenant_ids = []
        
        for group_name in ad_groups:
            if group_name in ad_group_mappings:
                mapping = ad_group_mappings[group_name]
                if isinstance(mapping, dict):
                    tenant_id = mapping.get("tenant_id")
                else:
                    tenant_id = mapping  # Direct mapping
                
                if tenant_id and tenant_id not in tenant_ids:
                    tenant_ids.append(tenant_id)
        
        return tenant_ids