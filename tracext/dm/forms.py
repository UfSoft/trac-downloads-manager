# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2009 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# License: BSD - Please view the LICENSE file for additional information.
# ==============================================================================

from trac.core import Component, implements
from trac.web.api import IRequestFilter, ITemplateStreamFilter
from trac.web.chrome import add_warning, add_notice
from genshi.filters.html import HTMLFormFiller


class FlashAndOrFill(Component):
    implements(IRequestFilter, ITemplateStreamFilter)

    # IRequestFilter methods
    def pre_process_request(self, req, handler):
        return handler

    def post_process_request(self, req, template, data, content_type):
        if 'dm_error' in req.session:
            add_warning(req, req.session.get('dm_error'))
            del req.session['dm_error']
            req.session.save()
        if 'dm_info' in req.session:
            add_notice(req, req.session.get('dm_info'))
            del req.session['dm_info']
            req.session.save()
        return template, data, content_type

    # ITemplateStreamFilter methods
    def filter_stream(self, req, method, filename, stream, data):
        if 'form_fill' in req.args:
            return stream | HTMLFormFiller(data=req.args)
        return stream

