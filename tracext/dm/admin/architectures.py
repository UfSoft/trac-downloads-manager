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
from tracext.dm.database import Architecture, architecture_table

class ArchitecturesAdmin(BaseOrderedItems, Component):
    implements(IAdminPanelProvider)
    env = log = config = None
    category_title = 'Architectures'
    category_class = Architecture
    category_table = architecture_table

    # IAdminPanelProvider methods
    def get_admin_panels(self, req):
        if 'TRAC_ADMIN' in req.perm:
            yield ('downloads', 'Downloads Manager', 'architectures',
                   'Architectures')
