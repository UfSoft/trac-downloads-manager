# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2009 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# License: BSD - Please view the LICENSE file for additional information.
# ==============================================================================

from trac.core import Component, implements
from trac.perm import IPermissionRequestor

class Permissions(Component):
    implements(IPermissionRequestor)

    # IPermissionRequestor methods
    def get_permission_actions(self):
        actions = ['DM_VIEW', 'DM_DOWNLOAD', 'DM_MANAGE']
        return actions + [('DM_ADMIN', actions)]
