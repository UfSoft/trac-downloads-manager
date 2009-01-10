# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2009 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# License: BSD - Please view the LICENSE file for additional information.
# ==============================================================================

import re

from genshi.builder import tag

from trac.core import Component, implements
from trac.util.translation import _
from trac.web import IRequestHandler, HTTPNotFound
from trac.web.chrome import INavigationContributor

from tracext.dm.database import (Architecture, Category, Download, DownloadType,
                                 Platform, session, Stat)

class Downloads(Component):
    implements(INavigationContributor, IRequestHandler)
    env = log = config = None # make pylint happy

    # INavigationContributor methods
    def get_active_navigation_item(self, req):
        yield 'downloads'

    def get_navigation_items(self, req):
        if 'DM_DOWNLOAD' in req.perm:
            yield ('mainnav', 'downloads', tag.a(_("Downloads"),
                                                 href=req.href.downloads()))

    # IRequestHandler methods
    def match_request(self, req):
        return re.match(r'^/downloads(?:/([0-9]+))?(?:/(.*))?$', req.path_info)

    def process_request(self, req):
        req.perm.require('DM_VIEW')
        match = re.match(r'^/downloads(?:/([0-9]+))?(?:/(.*))?$', req.path_info)
        print 1234, match.groups()
        download_id, download_filename = match.groups()

        Session = session(self.env)

        if not download_id:
            data = {'types': Session.query(DownloadType).count() > 0,
                    'platforms': Session.query(Platform).count() > 0,
                    'categories': Session.query(Category),
                    'architectures': Session.query(Architecture).count() > 0}
            return 'dm_downloads.html', data, None
        else:
            if not download_filename:
                raise HTTPNotFound
            self.send_file(req, download_id)

    def send_file(self, req, download_id):
        import os
        from datetime import datetime
        from trac.util.datefmt import http_date, localtz
        from trac.web.api import RequestDone
        from trac.web.wsgi import _FileWrapper
        import mimetypes

        Session = session(self.env)
        download = Session.query(Download).get(download_id)

        stat = os.stat(download.path)
        mtime = datetime.fromtimestamp(stat.st_mtime, localtz)
        last_modified = http_date(mtime)
        if last_modified == req.get_header('If-Modified-Since'):
            req.send_response(304)
            req.end_headers()
            raise RequestDone

        mimetype = mimetypes.guess_type(download.path)[0] or 'application/octet-stream'

        req.send_response(200)
        req.send_header('Content-Type', mimetype)
        req.send_header('Content-Length', stat.st_size)
        req.send_header('Last-Modified', last_modified)
        req.end_headers()

        if req.method != 'HEAD':
            fileobj = file(download.path, 'rb')
            file_wrapper = req.environ.get('wsgi.file_wrapper', _FileWrapper)
            buffer = fileobj.read(4096)
            try:
                while buffer:
                    print 'inside loop'
                    try:
                        req._write(buffer)
                        buffer = fileobj.read(4096)
                    except EOFError:
                        raise RequestDone
            except Exception, err:
                raise err
            else:
                download.stats.append(Stat(req.authname))
                Session.commit()
                print 'fooo'
            print '\n\n\n\nAfter'
        raise RequestDone
