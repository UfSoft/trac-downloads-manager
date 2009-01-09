# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2009 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# License: BSD - Please view the LICENSE file for additional information.
# ==============================================================================

from trac.core import Component, implements
from trac.admin.api import IAdminPanelProvider

from tracext.dm.admin.base import BaseOrderedItems
from tracext.dm.database import Platform, platform_table

class PlatformsAdmin(BaseOrderedItems, Component):
    implements(IAdminPanelProvider)
    env = log = config = None
    category_title = 'Platforms'
    category_class = Platform
    category_table = platform_table

    # IAdminPanelProvider methods
    def get_admin_panels(self, req):
        if 'TRAC_ADMIN' in req.perm:
            yield 'downloads', 'Downloads Manager', 'platforms', 'Platforms'
