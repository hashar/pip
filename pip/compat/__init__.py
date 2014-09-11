"""Stuff that differs in different Python versions and platform
distributions."""
from __future__ import absolute_import

# flake8: noqa

import os
import imp
import sys
import site

uses_pycache = hasattr(imp, 'cache_from_source')


console_encoding = sys.__stdout__.encoding


try:
    from logging.config import dictConfig as logging_dictConfig
except ImportError:
    from pip.compat.dictconfig import dictConfig as logging_dictConfig


if sys.version_info >= (3,):
    from urllib.request import url2pathname, urlretrieve, pathname2url
    import urllib.parse as urllib
    import urllib.request as urllib2
    import urllib.parse as urlparse

    def cmp(a, b):
        return (a > b) - (a < b)

    def console_to_str(s):
        try:
            return s.decode(console_encoding)
        except UnicodeDecodeError:
            return s.decode('utf_8')

    def native_str(s, replace=False):
        if isinstance(s, bytes):
            return s.decode('utf-8', 'replace' if replace else 'strict')
        return s

    def get_http_message_param(http_message, param, default_value):
        return http_message.get_param(param, default_value)

else:
    from urllib import url2pathname, urlretrieve, pathname2url
    import urllib
    import urllib2
    import urlparse

    def console_to_str(s):
        return s

    def native_str(s, replace=False):
        # Replace is ignored -- unicode to UTF-8 can't fail
        if isinstance(s, unicode):
            return s.encode('utf-8')
        return s

    def get_http_message_param(http_message, param, default_value):
        result = http_message.getparam(param)
        return result or default_value

    cmp = cmp


def get_path_uid(path):
    """
    Return path's uid.

    Does not follow symlinks:
        https://github.com/pypa/pip/pull/935#discussion_r5307003

    Placed this function in compat due to differences on AIX and
    Jython, that should eventually go away.

    :raises OSError: When path is a symlink or can't be read.
    """
    if hasattr(os, 'O_NOFOLLOW'):
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        file_uid = os.fstat(fd).st_uid
        os.close(fd)
    else:  # AIX and Jython
        # WARNING: time of check vulnerabity, but best we can do w/o NOFOLLOW
        if not os.path.islink(path):
            # older versions of Jython don't have `os.fstat`
            file_uid = os.stat(path).st_uid
        else:
            # raise OSError for parity with os.O_NOFOLLOW above
            raise OSError(
                "%s is a symlink; Will not return uid for symlinks" % path
            )
    return file_uid


# packages in the stdlib that may have installation metadata, but should not be
# considered 'installed'.  this theoretically could be determined based on
# dist.location (py27:`sysconfig.get_paths()['stdlib']`,
# py26:sysconfig.get_config_vars('LIBDEST')), but fear platform variation may
# make this ineffective, so hard-coding
stdlib_pkgs = ['python', 'wsgiref']
if sys.version_info >= (2, 7):
    stdlib_pkgs.extend(['argparse'])

# windows detection, covers cpython and ironpython
WINDOWS = sys.platform.startswith("win") \
          or (sys.platform == 'cli' and os.name == 'nt')
