# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2009 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# License: BSD - Please view the LICENSE file for additional information.
# ==============================================================================

from trac.web.chrome import add_stylesheet
from tracext.dm.database import session
from tracext.dm.utils import flash


class BaseOrderedItems(object):
    env = log = config = category_title = category_class = category_table = None

    # IAdminPanelProvider methods
    def get_admin_panels(self, req):
        if 'TRAC_ADMIN' in req.perm:
            yield ('dm', 'Downloads Manager', self.category_title.lower(),
                   self.category_title)

    def render_admin_panel(self, req, category, page, path_info):
        req.perm.require('TRAC_ADMIN')

        Session = session(self.env)
        data = {'dm_title': self.category_title}

        if req.method == 'POST':
            if path_info:
                if path_info != req.args.get('id'):
                    # Category ID changed, it's a PK which others use for FK, now what!?
                    pass
                # Edit Entry
                entry = Session.query(self.category_class).get(path_info)
                entry.id = req.args.get('id', path_info)
                entry.name = req.args.get('name')
                entry.description = req.args.get('description')
                Session.commit()
                req.redirect(req.href.admin(category, page))
            else:
                if 'selected' in req.args:
                    # Delete entries
                    Session.execute(self.category_table.delete().where(
                        self.category_class.id.in_(req.args.getlist('selected'))
                    ))
                    Session.commit()
                    flash(req, "Entries deleted")
#                    req.redirect(req.href.admin(category, page))
                elif 'create' in req.args:
                    if Session.query(self.category_class).get(
                                                            req.args.get('id')):
                        flash(req, "An entry by that ID already exists",
                              "error")
                        req.session.save()
                        req.args['form_fill'] = True
                        return 'admin/dm_ordered_entries.html', data.update(
                            {'query': Session.query(self.category_class).all()})
                    Session.add(
                        self.category_class(
                            req.args.get('name'),
                            req.args.get('id'),
                            req.args.get('description'),
                            Session.query(self.category_class).count()+1
                        )
                    )
                    Session.commit()
                    flash(req, "Entry added successfully")
                elif 'update' in req.args:
                    for key in [k for k in req.args.keys() if
                                                        k.startswith('order_')]:
                        entry = Session.query(self.category_class).get(key[6:])
                        entry.order = int(req.args.get(key))
                    Session.commit()
                    flash(req, "Order updated successfully")
                else:
                    flash(req, "Something wen't wrong", "error")

        if path_info:
            data.update(
                {'item': Session.query(self.category_class).get(path_info)}
            )
        else:
            data.update({'query': Session.query(self.category_class).all()})
        add_stylesheet(req, 'dm/css/dm.css')
        return 'admin/dm_ordered_entries.html', data
