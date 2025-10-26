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

import ldap3
import logging
from typing import Dict, List, Optional
from .oauth import OAuthClient, UserInfo


class ADClient(OAuthClient):
    def __init__(self, config):
        """
        Initialize the ADClient with Active Directory configuration.
        """
        # Store AD-specific config
        self.server_uri = config["server_uri"]
        self.domain = config["domain"]
        self.bind_dn = config.get("bind_dn")
        self.bind_password = config.get("bind_password")
        self.user_search_base = config["user_search_base"]
        self.group_search_base = config.get("group_search_base", config["user_search_base"])
        self.user_filter = config.get("user_filter", "(sAMAccountName={username})")
        self.group_filter = config.get("group_filter", "(member={user_dn})")
        self.group_mapping = config.get("group_mapping", {})
        self.auto_create_user = config.get("auto_create_user", True)
        self.default_tenant = config.get("default_tenant", None)
        
        # For compatibility with parent class, set dummy values
        self.client_id = config.get("client_id", "ad")
        self.client_secret = config.get("client_secret", "")
        self.authorization_url = config.get("authorization_url", "")
        self.token_url = config.get("token_url", "")
        self.userinfo_url = config.get("userinfo_url", "")
        self.redirect_uri = config.get("redirect_uri", "")
        self.scope = config.get("scope", "")
        
        # Connect to AD server
        try:
            self.server = ldap3.Server(self.server_uri, get_info=ldap3.ALL)
            self.connection = None
            self.connect()
        except Exception as e:
            logging.error(f"Failed to initialize ADClient: {e}")
            raise

    def connect(self):
        """
        Establish connection to the AD server.
        """
        try:
            if self.bind_dn and self.bind_password:
                # Use service account for binding
                self.connection = ldap3.Connection(
                    self.server, 
                    user=self.bind_dn, 
                    password=self.bind_password,
                    authentication=ldap3.SIMPLE,
                    auto_bind=True
                )
            else:
                # Anonymous binding
                self.connection = ldap3.Connection(
                    self.server,
                    auto_bind=True
                )
            logging.info(f"Successfully connected to AD server: {self.server_uri}")
        except ldap3.core.exceptions.LDAPException as e:
            logging.error(f"Failed to connect to AD server: {e}")
            raise ValueError(f"Failed to connect to AD server: {e}")

    def authenticate_user(self, username: str, password: str) -> bool:
        """
        Authenticate user against Active Directory.
        """
        try:
            # Search for the user in AD
            search_filter = self.user_filter.format(username=username)
            self.connection.search(
                search_base=self.user_search_base,
                search_filter=search_filter,
                attributes=['dn', 'sAMAccountName', 'mail', 'displayName', 'memberOf', 'givenName', 'sn']
            )
            
            if not self.connection.entries:
                logging.warning(f"User {username} not found in AD")
                return False
            
            user_entry = self.connection.entries[0]
            user_dn = user_entry.entry_dn
            
            # Bind with user credentials to verify password
            user_conn = ldap3.Connection(
                self.server,
                user=user_dn,
                password=password,
                authentication=ldap3.SIMPLE
            )
            
            authenticated = user_conn.bind()
            user_conn.unbind()
            
            if authenticated:
                logging.info(f"Successfully authenticated user {username} against AD")
            else:
                logging.warning(f"Failed to authenticate user {username} against AD")
            
            return authenticated
        except ldap3.core.exceptions.LDAPException as e:
            logging.error(f"AD authentication error for user {username}: {e}")
            return False

    def get_user_groups(self, username: str) -> List[str]:
        """
        Get all groups the user belongs to in AD.
        """
        try:
            # Search for the user in AD
            search_filter = self.user_filter.format(username=username)
            self.connection.search(
                search_base=self.user_search_base,
                search_filter=search_filter,
                attributes=['dn', 'memberOf']
            )
            
            if not self.connection.entries:
                logging.warning(f"User {username} not found in AD for group lookup")
                return []
            
            user_entry = self.connection.entries[0]
            user_dn = user_entry.entry_dn
            
            # If user has memberOf attribute, return those groups
            member_of = getattr(user_entry, 'memberOf', [])
            if member_of:
                groups = []
                for group_dn in member_of:
                    # Extract group name from DN
                    group_name = self._extract_cn_from_dn(str(group_dn))
                    groups.append(group_name)
                return groups
            else:
                # Fallback: search for groups that have this user as member
                search_filter = self.group_filter.format(user_dn=user_dn)
                self.connection.search(
                    search_base=self.group_search_base,
                    search_filter=search_filter,
                    attributes=['cn', 'name', 'sAMAccountName']
                )
                
                groups = []
                for entry in self.connection.entries:
                    if hasattr(entry, 'cn'):
                        groups.append(str(entry.cn))
                    elif hasattr(entry, 'name'):
                        groups.append(str(entry.name))
                    elif hasattr(entry, 'sAMAccountName'):
                        groups.append(str(entry.sAMAccountName))
                
                return groups
        except ldap3.core.exceptions.LDAPException as e:
            logging.error(f"Error fetching groups for user {username}: {e}")
            return []

    def _extract_cn_from_dn(self, dn: str) -> str:
        """
        Extract the CN (Common Name) from a DN (Distinguished Name).
        """
        parts = dn.split(',')
        for part in parts:
            part = part.strip()
            if part.lower().startswith('cn='):
                return part[3:]  # Remove 'CN=' prefix
        # If no CN found, return the full DN or the last part
        return dn.split(',')[-1].strip()[3:] if dn.lower().startswith('cn=') else dn

    def get_user_info(self, username: str) -> Dict:
        """
        Fetch user information from AD.
        """
        try:
            search_filter = self.user_filter.format(username=username)
            self.connection.search(
                search_base=self.user_search_base,
                search_filter=search_filter,
                attributes=['mail', 'sAMAccountName', 'displayName', 'givenName', 'sn', 'memberOf', 'telephoneNumber', 'department', 'title']
            )
            
            if not self.connection.entries:
                return {}
            
            user_entry = self.connection.entries[0]
            
            # Extract user info
            email = str(user_entry.mail[0]) if hasattr(user_entry, 'mail') and user_entry.mail else f"{username}@{self.domain}"
            display_name = str(user_entry.displayName[0]) if hasattr(user_entry, 'displayName') and user_entry.displayName else username
            first_name = str(user_entry.givenName[0]) if hasattr(user_entry, 'givenName') and user_entry.givenName else ""
            last_name = str(user_entry.sn[0]) if hasattr(user_entry, 'sn') and user_entry.sn else ""
            full_name = f"{first_name} {last_name}".strip() or display_name
            telephone = str(user_entry.telephoneNumber[0]) if hasattr(user_entry, 'telephoneNumber') and user_entry.telephoneNumber else ""
            department = str(user_entry.department[0]) if hasattr(user_entry, 'department') and user_entry.department else ""
            title = str(user_entry.title[0]) if hasattr(user_entry, 'title') and user_entry.title else ""

            return {
                "email": email,
                "username": str(user_entry.sAMAccountName[0]),
                "nickname": full_name,
                "name": full_name,
                "first_name": first_name,
                "last_name": last_name,
                "telephone": telephone,
                "department": department,
                "title": title,
                "groups": self.get_user_groups(username)
            }
        except ldap3.core.exceptions.LDAPException as e:
            logging.error(f"Error fetching user info for {username}: {e}")
            return {}

    def fetch_user_info(self, access_token, **kwargs):
        """
        For AD authentication, we'll get user info during authentication process.
        This is a compatibility method for the OAuth interface.
        """
        # This method is typically called with an access token, 
        # but for AD we work with usernames/passwords
        username = kwargs.get('username', '')
        if username:
            user_info = self.get_user_info(username)
            return self.normalize_user_info(user_info)
        return super().fetch_user_info(access_token, **kwargs)

    def normalize_user_info(self, user_info):
        email = user_info.get("email", "")
        username = user_info.get("username", str(email).split("@")[0] if email else "unknown")
        nickname = user_info.get("nickname", username)
        avatar_url = user_info.get("avatar_url", "")
        
        # Add AD-specific info
        ad_groups = user_info.get("groups", [])
        first_name = user_info.get("first_name", "")
        last_name = user_info.get("last_name", "")
        telephone = user_info.get("telephone", "")
        department = user_info.get("department", "")
        title = user_info.get("title", "")
        
        normalized = super().normalize_user_info({
            "email": email,
            "username": username,
            "nickname": nickname,
            "avatar_url": avatar_url
        })
        
        # Add AD groups and other AD-specific attributes to the normalized user info
        normalized.ad_groups = ad_groups
        normalized.first_name = first_name
        normalized.last_name = last_name
        normalized.telephone = telephone
        normalized.department = department
        normalized.title = title
            
        return normalized