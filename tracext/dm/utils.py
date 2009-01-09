# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2009 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# License: BSD - Please view the LICENSE file for additional information.
# ==============================================================================

import hashlib
import os
import re
import unicodedata
from tracext.dm._dynamic.translit_tab import (LONG_TABLE, SHORT_TABLE,
                                              SINGLE_TABLE)

_punctuation_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def gen_slug(text, delim='-'):
    result = []
    for word in _punctuation_re.split(text.lower()):
        word = _punctuation_re.sub(u'', transliterate(word))
        if word:
            result.append(word)
    return unicode(delim.join(result))

def transliterate(string, table='long'):
    """Transliterate to 8 bit using one of the tables given.  The table
    must either be ``'long'``, ``'short'`` or ``'single'``.
    """
    table = {
        'long':     LONG_TABLE,
        'short':    SHORT_TABLE,
        'single':   SINGLE_TABLE
    }[table]
    return unicodedata.normalize('NFKC', unicode(string)).translate(table)


def flash(req, msg, type='info'):
    if type not in ('error', 'info'):
        raise Exception("Flash type can only be 'error' or 'info'")
    req.session["dm_%s" % type] = msg
    req.session.save()

def md5sum(filepath):
    try:
        file = open(filepath, 'rb')
        md5 = hashlib.md5()
        buffer = file.read(2<<20)
        while buffer:
            md5.update(buffer)
            buffer = file.read(2<<20)
        file.close()
        return md5.hexdigest()
    except Exception, err:
        raise err

def build_path(basepath, category, architecture, version, filename):
    return os.path.join(basepath, category, architecture, version, filename)
