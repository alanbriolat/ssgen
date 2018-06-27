import os
import os.path
import fnmatch
from functools import partial
from itertools import ifilter


DEFAULT_EXCLUDE = ['.*', '_*', '*~']
DEFAULT_INCLUDE = ['.htaccess']


def fnmatchany(path, patterns):
    """Check if *path* matches at least one of *patterns*."""
    for pattern in patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
    return False


def is_visible(path, exclude, include):
    """Check if *path* should be visible based on the filename.

    Patterns in *include* take precedence over those in *exclude*, so something
    excluded by a pattern can be made explicitly visible (e.g. ``.htaccess``).
    """
    fn = os.path.basename(path)
    return (not fnmatchany(fn, exclude)) or fnmatchany(fn, include)


def walk(root, exclude=[], include=[]):
    """Generate a list of visible files in *root*.
    
    All file paths are relative to *root*.
    """
    visible_filter = partial(is_visible,
                             exclude=DEFAULT_EXCLUDE + exclude,
                             include=DEFAULT_INCLUDE + include)
    for root_, dirs, files in os.walk(root):
        relroot = os.path.relpath(root_, root)
        # Don't recurse into non-visible directories
        dirs[:] = filter(visible_filter, dirs)
        # Return visible files
        for f in ifilter(visible_filter, files):
            yield os.path.normpath(os.path.join(relroot, f))


class Directory(object):
    def __init__(self, path):
        self.path = path

    def __iter__(self):
        return (File(f, self) for f in walk(self.path))


class File(dict):
    def __init__(self, path, parent):
        self.path = path
        self.parent = parent

    @property
    def fullpath(self):
        return os.path.join(self.parent.path, self.path)
