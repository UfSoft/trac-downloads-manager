# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2009 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# License: BSD - Please view the LICENSE file for additional information.
# ==============================================================================

from setuptools import setup
import tracext.dm as tracdm

setup(name=tracdm.__package__,
      version=tracdm.__version__,
      author=tracdm.__author__,
      author_email=tracdm.__email__,
      url=tracdm.__url__,
      download_url='http://python.org/pypi/%s' % tracdm.__package__,
      description=tracdm.__summary__,
      long_description=tracdm.__description__,
      license=tracdm.__license__,
      platforms="OS Independent - Anywhere Python and Trac >=0.11 is known to run.",
      install_requires = ['Trac>0.11', 'Genshi>=0.5', 'Babel',
                          'TracSQLAlchemyBridge>=0.1.2'],
      setup_requires = ['TracSQLAlchemyBridge'],
      keywords = "trac plugin downloads manager",
      packages=['tracext', 'tracext.dm'],
      namespace_packages=['tracext'],
      package_data={
        'tracext.dm': [
            'templates/*.html',
            'htdocs/css/*.css',
            'htdocs/img/*.png',
            'htdocs/img/*.gif',
            'htdocs/js/*.js',
        ]
      },
      message_extractors = {
        'tracext.dm': [
            ('**.py', 'python', None),
            ('**/templates/**.html', 'genshi', None),
            ('public/**', 'ignore', None)
        ]
      },
      entry_points = {
        'trac.plugins': [
            'tracext.dm = tracext.dm',
        ],
        'distutils.commands': [
            'extract = babel.messages.frontend:extract_messages',
            'init = babel.messages.frontend:init_catalog',
            'compile = babel.messages.frontend:compile_catalog',
            'update = babel.messages.frontend:update_catalog'
        ]
      },
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Text Processing',
          'Topic :: Utilities',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ]
)
