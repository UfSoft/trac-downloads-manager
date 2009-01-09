# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2009 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# License: BSD - Please view the LICENSE file for additional information.
# ==============================================================================

import os.path
import time
#from datetime import datetime

import sqlalchemy as sqla
from sqlalchemy.orm import (mapper, relation, dynamic_loader, MapperExtension,
                            EXT_CONTINUE, EXT_STOP)
from sqlalchemy.orm.session import object_session
from tracext.sa import session
from tracext.dm.utils import gen_slug, md5sum, build_path

name = 'trac-downloads-manager'
version = 1

metadata = sqla.MetaData()

class CustomMapper(MapperExtension):
    def before_insert(self, mapper, connection, instance):
        env = object_session(instance).trac_env
        filepath = os.path.join(env.config.get('downloads', 'path', ''),
                            instance.category.id, instance.architecture.id,
                            instance.version, instance.filename)
        instance.md5 = md5sum(filepath)
#        print '\n\n\n', instance
#        print instance.__dict__
#        print object_session(instance).trac_env
        return EXT_CONTINUE
#        return MapperExtension.before_insert(self, mapper, connection, instance)

    def before_update(self, mapper, connection, instance):
#        print '\n\n\n', instance
#        print instance.__dict__
#        if object_session(instance).is_modified(instance,
#                                                include_collections=False):
#            print 'foo'
        return EXT_CONTINUE
#        return MapperExtension.before_update(self, mapper, connection, instance)

category_table = sqla.Table('dm_category', metadata,
    sqla.Column('id', sqla.Text, primary_key=True),
    sqla.Column('name', sqla.Text, nullable=False, unique=True),
    sqla.Column('description', sqla.Text),
    sqla.Column('order', sqla.Integer),
)

architecture_table = sqla.Table('dm_architecture', metadata,
    sqla.Column('id', sqla.Text, primary_key=True),
    sqla.Column('name', sqla.Text, nullable=False, unique=True),
    sqla.Column('description', sqla.Text),
    sqla.Column('order', sqla.Integer),
)

platform_table = sqla.Table('dm_platform', metadata,
    sqla.Column('id', sqla.Text, primary_key=True),
    sqla.Column('name', sqla.Text, nullable=False, unique=True),
    sqla.Column('description', sqla.Text),
    sqla.Column('order', sqla.Integer),
)

download_type_table = sqla.Table('dm_download_type', metadata,
    sqla.Column('id', sqla.Text, primary_key=True),
    sqla.Column('name', sqla.Text, nullable=False, unique=True),
    sqla.Column('description', sqla.Text),
    sqla.Column('order', sqla.Integer),
)

download_table = sqla.Table('dm_download', metadata,
    sqla.Column('id', sqla.Integer, primary_key=True, autoincrement=True),
    sqla.Column('filename', sqla.Text, nullable=False),
    sqla.Column('description', sqla.Text),
    sqla.Column('size', sqla.Integer, nullable=False),
    sqla.Column('timestamp', sqla.Integer, default=time.time),
    sqla.Column('uploader', sqla.Text, nullable=False),
    sqla.Column('component', sqla.Text, nullable=False),
    sqla.Column('version', sqla.Text, nullable=False),
    sqla.Column('md5', sqla.Text(32), nullable=False),
    sqla.Column('hidden', sqla.Boolean, nullable=False, default=False),
    sqla.Column('category_id', None,
                sqla.ForeignKey('dm_category.id', onupdate="cascade")),
    sqla.Column('architecture_id', None,
                sqla.ForeignKey('dm_architecture.id', onupdate="cascade")),
    sqla.Column('platform_id', None,
                sqla.ForeignKey('dm_platform.id', onupdate="cascade")),
    sqla.Column('type_id', None,
                sqla.ForeignKey('dm_download_type.id', onupdate="cascade")),
    sqla.UniqueConstraint('filename', 'size', 'version', 'md5',
                          'architecture_id', 'platform_id', 'type_id')
)

stats_table = sqla.Table('dm_stats', metadata,
    sqla.Column('timestamp', sqla.Integer, default=time.time, primary_key=True),
    sqla.Column('user', sqla.Text, nullable=False),
    sqla.Column('download_id', None, sqla.ForeignKey('dm_download.id')),
)
class Category(object):
    id = name = description = order = downloads = None
    def __init__(self, name, slug=None, description=u'', order=None):
        self.name = name
        self.id = slug or gen_slug(name)
        self.description = description
        self.order = order or self._get_order()

    def _get_order(self):
        # Grab an items count from this table on database
        return 1

class Architecture(object):
    def __init__(self, name, slug=None, description=u'', order=None):
        self.name = name
        self.description = description
        self.id = slug or gen_slug(name)
        self.order = order or self._get_order()

    def _get_order(self):
        # Grab an items count from this table on database
        return 1

class Platform(object):
    def __init__(self, name, slug=None, description=u'', order=None):
        self.name = name
        self.description = description
        self.id = slug or gen_slug(name)
        self.order = order or self._get_order()

    def _get_order(self):
        # Grab an items count from this table on database
        return 1

class DownloadType(object):
    def __init__(self, name, slug=None, description=u'', order=None):
        self.name = name
        self.description = description
        self.id = gen_slug(slug or name)
        self.order = order or self._get_order()

    def _get_order(self):
        # Grab an items count from this table on database
        return 1

class Stat(object):
    def __init__(self, username):
        self.user = username

class Download(object):
    filename = description = size = uploader = component = version = md5 = None
    stats = category = architecture = hidden = None
    def __init__(self, filename, description=u'', size=None, uploader=None,
                 component=None, version=None):
        self.filename = filename
        self.description = description
        self.size = size
        self.uploader = uploader
        self.component = component
        self.version = version
        self.hidden = False
#        self.md5 = md5sum(self.path)

    def count(self):
        return self.stats.count()

    @property
    def path(self):
        env = object_session(self).trac_env
        return os.path.join(env.config.get('downloads', 'path', ''),
                            self.category.id, self.architecture.id,
                            self.version, self.filename)

mapper(Category, category_table,
       order_by=[category_table.c.order, category_table.c.name],
       properties = dict(
            downloads = relation(Download, backref='category')
       )
)
mapper(Architecture, architecture_table,
       order_by=[architecture_table.c.order, architecture_table.c.name],
       properties = dict(
            downloads = relation(Download, backref='architecture')
       )
)
mapper(Platform, platform_table,
       order_by=[platform_table.c.order, platform_table.c.name],
       properties = dict(
            downloads = relation(Download, backref='platform')
       )
)
mapper(DownloadType, download_type_table,
       order_by=[download_type_table.c.order, download_type_table.c.name],
       properties = dict(
            downloads = relation(Download, backref='type')
       )
)
mapper(Stat, stats_table)
mapper(Download, download_table, extension=CustomMapper(),
       properties=dict(
            stats = dynamic_loader(Stat, backref='download')
       ),
)
