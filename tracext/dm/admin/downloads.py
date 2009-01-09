# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2009 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# License: BSD - Please view the LICENSE file for additional information.
# ==============================================================================

import os
from stat import ST_SIZE
from shutil import copyfileobj
import unicodedata
from trac.core import Component, implements
from trac.admin.api import IAdminPanelProvider
from trac.util.text import to_unicode
from trac.web.chrome import add_script

from tracext.dm.database import (session, Category, category_table, Download,
                                 download_table, Architecture, Platform,
                                 DownloadType)
from tracext.dm.utils import flash, build_path, md5sum

class DownloadsAdmin(Component):
    implements(IAdminPanelProvider)
    env = config = log = None

    # IAdminPanelProvider methods
    def get_admin_panels(self, req):
        if 'TRAC_ADMIN' in req.perm:
            yield 'downloads', 'Downloads Manager', 'downloads', 'Downloads'

    def render_admin_panel(self, req, category, page, path_info):
        req.perm.require('TRAC_ADMIN')

        # Keep the session opened until page renders
        #req.args['Session'] =
        Session = session(self.env)

        if req.method == 'POST':
            if path_info:
                # Edit Download
                download_id = int(path_info)
                download = Session.query(Download).get(download_id)
                for key, value in req.args.iteritems():
                    if hasattr(download, key):
                        setattr(download, key, value)
                Session.commit()
            else:
                if 'selected' in req.args:
                    # Delete downloads
                    pass
                elif 'add' in req.args:
                    # File uploaded
                    file = req.args.get('file')
                    if not hasattr(file, 'filename') or not file.filename:
                        flash(req, "No file uploaded", "error")
                        req.args['form_fill'] = True

                    # File size
                    if hasattr(file.file, 'fileno'):
                        size = os.fstat(file.file.fileno())[ST_SIZE]
                    else:
                        size = file.file.len
                    if size == 0:
                        flash(req, "Can't upload empty file", "error")
                        req.args['form_fill'] = True

                    if 'form_fill' not in req.args:
                        filename = unicodedata.normalize(
                            'NFC', to_unicode(file.filename, 'utf-8'))
                        filename = filename.replace('\\', '/').replace(':', '/')
                        filename = os.path.basename(filename)
                        download = Download(
                            filename,
                            description=req.args.get('description', ''),
                            size=size,
                            uploader=req.authname,
                            component=req.args.get('component', ''),
                            version=req.args.get('version', '0')
                        )
#                        import datetime
#                        download.timestamp = datetime.datetime.utcnow()
                        platform = req.args.get('platform')
                        download.category = Session.query(Category).get(req.args.get('category'))
                        if platform:
                            download.platform = Session.query(Platform).get(platform)
                        architecture = req.args.get('architecture')
                        if architecture:
                            download.architecture = Session.query(Architecture).get(architecture)
                        dtype = req.args.get('type')
                        if dtype:
                            download.type = Session.query(DownloadType).get(dtype)
#                        download.md5 = '5165e2fcd2cf58899f34878fe6b447c6'
                        filepath = build_path(
                            self.config.get('downloads', 'path'),
                            download.category.id,
                            download.architecture.id,
                            download.version,
                            download.filename
                        )
                        try:
                            if not os.path.isdir(os.path.dirname(filepath)):
                                os.makedirs(os.path.dirname(filepath))
                            outfile = open(filepath, "wb+")
                            copyfileobj(file.file, outfile)
                            outfile.close()
                        except Exception, err:
                            raise err
#                            Session.rollback()

                        finally:
                            download.md5 = md5sum(filepath)
                            Session.commit()
                            flash(req, "File successfully uploaded")
                elif 'update' in req.args:
                    # hmm, no order here, skip this elif?
                    pass

        data = {'types': Session.query(DownloadType),
                'platforms': Session.query(Platform),
                'architectures': Session.query(Architecture)}

        if self.config.getbool('downloads', 'link_versions') or \
                            self.config.getbool('downloads', 'link_components'):
            print '\n\n\n', 123
            db = self.env.get_db_cnx()
            cursor = db.cursor()
            if self.config.getbool('downloads', 'link_versions'):
                cursor.execute("SELECT name, description FROM version")
                data.update({'versions': [name for (name, desc) in cursor]})
            if self.config.getbool('downloads', 'link_components'):
                cursor.execute("SELECT name, description FROM component")
                data.update({'components': [name for (name, desc) in cursor]})


        if path_info:
            data.update({'item': Session.query(Download).get(int(path_info))})
        else:
            data.update({'categories': Session.query(Category)})

        print 555
        print Session.query(Download).all()
        print 555
        for c in data['categories'].all():
            print '\n\n', c
            print c.downloads
        add_script(req, 'dm/js/dm.js')
        return 'admin/dm_downloads.html', data
