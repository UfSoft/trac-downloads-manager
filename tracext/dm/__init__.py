# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2009 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# License: BSD - Please view the LICENSE file for additional information.
# ==============================================================================
"""
Foo Bar DOC
"""

__version__     = '0.1.0'
__author__      = 'Pedro Algarvio'
__email__       = 'ufs@ufsoft.org'
__package__     = 'TracDownloadsManager'
__license__     = 'BSD'
__url__         = 'http://trac-hacks.org/wiki/TracSqlAlchemyBridgeIntegration'
__summary__     = 'Trac downloads manager plugin'
__description__ = __doc__

# ------------------------- import package modules -----------------------------
import admin, database, forms
# ----------------------- Import non-package modules ---------------------------
import pkg_resources
from trac.core import Component, implements
from trac.config import Option, BoolOption
from trac.env import IEnvironmentSetupParticipant
from trac.web.chrome import ITemplateProvider
from tracext.sa import engine, session
# ----------------------- Database Init/Upgrade Code ---------------------------
class DownloadsManagerSetup(Component):
    implements(IEnvironmentSetupParticipant)
    env = log = config = None # Make pylint happier

    # IEnvironmentSetupParticipant methods
    def environment_created(self):
        self.found_db_version = 0
        self.upgrade_environment(self.env.get_db_cnx())

    def environment_needs_upgrade(self, db):
        cursor = db.cursor()
        cursor.execute("SELECT value FROM system WHERE name=%s",
                       (database.name,))
        value = cursor.fetchone()
        if not value:
            self.found_db_version = 0
            return True
        else:
            self.found_db_version = int(value[0])
            self.log.debug("%s: Found db version %s, current is %s",
                           __package__, self.found_db_version, database.version)
            return self.found_db_version < database.version

    def upgrade_environment(self, db):
        # Currently we only create the tables, so far there's no migration done
        database.metadata.create_all(bind=engine(self.env))
        cursor = db.cursor()
        if not self.found_db_version:
            cursor.execute("INSERT INTO system (name, value) VALUES (%s, %s)",
                           (database.name, database.version))
        else:
            cursor.execute("UPDATE system SET value=%s WHERE name=%s",
                           (database.version, database.name))
        self.log.info("Inserting example data")
        Session = session(self.env)
        Session.add_all([
            database.Category('Downloads', 'downloads',
                              "Project files to download", 1),
            database.DownloadType('source', description='source code', order=1),
            database.DownloadType('binary', description='compiled packaged',
                                  order=2)
        ] + [database.Architecture(name, order=idx+1) for idx, name in
             enumerate(('Alpha', 'Arm', 'i386', 'ia64', 'PowerPC',
                       'Sparc', 'Other'))
        ] + [database.Platform(name, order=idx+1) for idx, name in
             enumerate(('Windows', 'Linux', 'MacOS', 'Other'))
        ])
        Session.commit()

# -----------------------------  Resources Code --------------------------------
class DownloadsManagerResources(Component):
    implements(ITemplateProvider)
    # ITemplateProvider methods
    def get_templates_dirs(self):
        return [pkg_resources.resource_filename(__name__, 'templates')]

    def get_htdocs_dirs(self):
        return [('dm', pkg_resources.resource_filename(__name__, 'htdocs'))]

# ---------------------------- Configuration Code ------------------------------
class DownloadsConfiguration(Component):
    link_versions = BoolOption('downloads', 'link_versions', default=True,
                               doc="Link versions from ticket system")
    link_components = BoolOption('downloads', 'link_components', default=True,
                                 doc="Link components from ticket system")
    path = Option('downloads', 'path', 'downloads',
                  doc="Path to the downloads base directory.")
