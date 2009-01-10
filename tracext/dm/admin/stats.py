# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2009 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# License: BSD - Please view the LICENSE file for additional information.
# ==============================================================================

from trac.core import Component, implements
from trac.admin.api import IAdminPanelProvider
from tracext.dm.database import Stat, stats_table

class StatsAdmin(Component):
    implements(IAdminPanelProvider)

    # IAdminPanelProvider methods
    def get_admin_panels(self, req):
        if 'TRAC_ADMIN' in req.perm:
            yield 'dm', 'Downloads Manager', 'stats', 'Statistics'

    def render_admin_panel(self, req, category, page, path_info):
        req.perm.require('TRAC_ADMIN')
