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
from trac.web.chrome import add_script, add_stylesheet

from tracext.dm.database import (session, Category, category_table, Download,
                                 download_table, Architecture, Platform,
                                 DownloadType)
from tracext.dm.utils import flash, build_path, md5sum

class DownloadsAdmin(Component):
    implements(IAdminPanelProvider)
    env = config = log = None

    # IAdminPanelProvider methods
    def get_admin_panels(self, req):
        if 'DM_MANAGE' in req.perm:
            yield 'dm', 'Downloads Manager', 'downloads', 'Downloads'

    def render_admin_panel(self, req, category, page, path_info):
        req.perm.require('DM_MANAGE')

        # Keep the session opened until page renders
        #req.args['Session'] =
        Session = session(self.env)

        data = {'admin': {'category': category, 'page': page}}

        if req.method == 'POST':
            if 'edit' in req.args:
                # Edit Download
                download_id = int(path_info)
                download = Session.query(Download).get(download_id)

                dlcategory = req.args.get('category')
                if download.category.id != dlcategory:
                    # Category changed, let's update to the new one
                    dlcategory = Session.query(Category).get(dlcategory)
                    download.category = dlcategory

                architecture = req.args.get('architecture')
                if architecture and download.architecture.id != architecture:
                    # Architecture changed, let's update to the new one
                    architecture = Session.query(Architecture).get(architecture)
                    download.architecture = architecture

                platform = req.args.get('platform')
                if platform and download.platform.id != platform:
                    # Platform changed, let's update to the new one
                    platform = Session.query(Platform).get(platform)
                    download.platform = platform

                dltype = req.args.get('type')
                if dltype and download.type.id != dltype:
                    # Type changed, let's update to the new one
                    dltype = Session.query(DownloadType).get(dltype)
                    download.type = dltype

                component = req.args.get('component')

                download.description = req.args.get('description')
                download.uploader = req.authname
                download.component = req.args.get('component', u'')
                download.version = req.args.get('version', u'')
                download.hidden = req.args.get('hidden', 'no') == 'yes'

                file = req.args.get('file')
                if hasattr(file, 'filename') and file.filename:
                    # File uploaded ? Get File size
                    if hasattr(file.file, 'fileno'):
                        size = os.fstat(file.file.fileno())[ST_SIZE]
                    else:
                        size = file.file.len
                    if size == 0:
                        flash(req, "Can't upload empty file", "error")
                        req.args['form_fill'] = True

                    if 'form_fill' not in req.args:
                        filename = unicodedata.normalize(
                            'NFC', to_unicode(file.filename, 'utf-8')
                        )
                        filename = filename.replace('\\', '/').replace(':', '/')
                        filename = os.path.basename(filename)
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
                        download.filename = filename
                if 'form_fill' not in req.args:
                    Session.commit()
                    flash(req, "Entry updated successfully.")
                    req.redirect(req.href.admin(category, page))
            elif 'delete' in req.args:
                # Delete downloads
                if req.args.getlist('selected'):
                    for id in req.args.getlist('selected'):
                        # One by one so that MapperExtension.after_delete()
                        # get's called :\, oh well, SQLAlchemy is still
                        # GREAT!
                        entry = Session.query(Download).get(int(id))
                        Session.delete(entry)
                    Session.commit()
                    flash(req, "Entries deleted")
                else:
                    flash(req, "Nothing selected, nothing deleted")
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
                        uploader=req.authname,
                        component=req.args.get('component', ''),
                        version=req.args.get('version', '0')
                    )
                    download.hidden = req.args.get('hidden', 'no') == 'yes'
                    platform = req.args.get('platform')
                    download.category = Session.query(Category) \
                                                .get(req.args.get('category'))
                    if platform:
                        download.platform = Session.query(Platform)\
                                                                .get(platform)
                    architecture = req.args.get('architecture')
                    if architecture:
                        download.architecture = Session.query(Architecture)\
                                                            .get(architecture)
                    dtype = req.args.get('type')
                    if dtype:
                        download.type = Session.query(DownloadType).get(dtype)
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
                        Session.commit()
                        flash(req, "File successfully uploaded")
            elif 'update' in req.args:
                # hmm, no order here, skip this elif?
                pass
        if path_info:
            data.update(
                {'download': Session.query(Download).get(int(path_info))}
            )

        data.update({'types': Session.query(DownloadType),
                     'platforms': Session.query(Platform),
                     'categories': Session.query(Category),
                     'architectures': Session.query(Architecture)})

        if self.config.getbool('downloads', 'link_versions') or \
                            self.config.getbool('downloads', 'link_components'):
            db = self.env.get_db_cnx()
            cursor = db.cursor()
            if self.config.getbool('downloads', 'link_versions'):
                cursor.execute("SELECT name, description FROM version")
                data.update({'versions': [name for (name, desc) in cursor]})
            if self.config.getbool('downloads', 'link_components'):
                cursor.execute("SELECT name, description FROM component")
                data.update({'components': [name for (name, desc) in cursor]})

        add_script(req, 'dm/js/dm.js')
        add_stylesheet(req, 'dm/css/dm.css')
        return 'admin/dm_downloads.html', data
