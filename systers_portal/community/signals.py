from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404

from community.constants import COMMUNITY_ADMIN
from community.models import Community
from community.utils import (create_groups, assign_permissions, remove_groups)


@receiver(post_save, sender=Community, dispatch_uid="create_groups")
def manage_community_groups(sender, instance, created, **kwargs):
    """Manage user groups and user permissions for a particular Community"""
    name = instance.name
    if created:
        groups = create_groups(name)
        assign_permissions(instance, groups)
        community_admin_group = next(
            g for g in groups if g.name == COMMUNITY_ADMIN.format(name))
        instance.community_admin.join_group(community_admin_group)
    else:
        if name != instance.original_name:
            remove_groups(instance.original_name)
            groups = create_groups(name)
            assign_permissions(instance, groups)
        if instance.community_admin != instance.original_community_admin:
            community_admin_group = \
                get_object_or_404(Group, name=COMMUNITY_ADMIN.format(name))
            instance.original_community_admin.leave_group(
                community_admin_group)
            instance.community_admin.join_group(community_admin_group)