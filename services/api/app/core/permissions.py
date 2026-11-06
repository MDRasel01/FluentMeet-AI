from enum import Enum
from typing import Dict, Set, List

class PlatformRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    SUPPORT_ADMIN = "support_admin"
    PLATFORM_ANALYST = "platform_analyst"
    INDIVIDUAL = "individual"

class OrgRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"

class OrgPermission(str, Enum):
    VIEW_ORGANIZATION = "org:view"
    EDIT_ORGANIZATION_SETTINGS = "org:edit_settings"
    INVITE_MEMBERS = "org:invite_members"
    REMOVE_MEMBERS = "org:remove_members"
    CHANGE_MEMBER_ROLES = "org:change_roles"
    VIEW_TEAM_ANALYTICS = "org:view_analytics"
    VIEW_REPORTS = "org:view_reports"
    MANAGE_SUBSCRIPTION = "org:manage_subscription"
    TRANSFER_OWNERSHIP = "org:transfer_ownership"
    DELETE_ORGANIZATION = "org:delete"

# Hierarchical rank for role-escalation prevention (Higher number = higher rank)
ROLE_HIERARCHY: Dict[OrgRole, int] = {
    OrgRole.OWNER: 40,
    OrgRole.ADMIN: 30,
    OrgRole.MANAGER: 20,
    OrgRole.MEMBER: 10,
}

# Permission matrix per organization role
ORG_ROLE_PERMISSIONS: Dict[OrgRole, Set[OrgPermission]] = {
    OrgRole.OWNER: {
        OrgPermission.VIEW_ORGANIZATION,
        OrgPermission.EDIT_ORGANIZATION_SETTINGS,
        OrgPermission.INVITE_MEMBERS,
        OrgPermission.REMOVE_MEMBERS,
        OrgPermission.CHANGE_MEMBER_ROLES,
        OrgPermission.VIEW_TEAM_ANALYTICS,
        OrgPermission.VIEW_REPORTS,
        OrgPermission.MANAGE_SUBSCRIPTION,
        OrgPermission.TRANSFER_OWNERSHIP,
        OrgPermission.DELETE_ORGANIZATION,
    },
    OrgRole.ADMIN: {
        OrgPermission.VIEW_ORGANIZATION,
        OrgPermission.EDIT_ORGANIZATION_SETTINGS,
        OrgPermission.INVITE_MEMBERS,
        OrgPermission.REMOVE_MEMBERS,
        OrgPermission.CHANGE_MEMBER_ROLES,
        OrgPermission.VIEW_TEAM_ANALYTICS,
        OrgPermission.VIEW_REPORTS,
        OrgPermission.MANAGE_SUBSCRIPTION,
    },
    OrgRole.MANAGER: {
        OrgPermission.VIEW_ORGANIZATION,
        OrgPermission.INVITE_MEMBERS,
        OrgPermission.VIEW_TEAM_ANALYTICS,
        OrgPermission.VIEW_REPORTS,
    },
    OrgRole.MEMBER: {
        OrgPermission.VIEW_ORGANIZATION,
        OrgPermission.VIEW_REPORTS,
    },
}

def has_org_permission(role: str, permission: OrgPermission) -> bool:
    try:
        org_role = OrgRole(role)
        return permission in ORG_ROLE_PERMISSIONS.get(org_role, set())
    except ValueError:
        return False

def can_manage_target_role(actor_role: str, target_role: str) -> bool:
    """
    Prevent privilege escalation.
    An actor can only manage/assign roles that have a strictly lower rank than their own.
    Only the Owner can transfer ownership.
    """
    try:
        a_role = OrgRole(actor_role)
        t_role = OrgRole(target_role)
        if a_role == OrgRole.OWNER:
            return True
        return ROLE_HIERARCHY[a_role] > ROLE_HIERARCHY[t_role]
    except (ValueError, KeyError):
        return False
