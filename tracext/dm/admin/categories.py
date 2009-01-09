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
from tracext.dm.database import Category, category_table


class CategoriesAdmin(BaseOrderedItems, Component):
    implements(IAdminPanelProvider)
    env = log = config = None
    category_title = 'Categories'
    category_class = Category
    category_table = category_table

    # IAdminPanelProvider methods
    def get_admin_panels(self, req):
        if 'TRAC_ADMIN' in req.perm:
            yield 'downloads', 'Downloads Manager', 'categories', 'Categories'

