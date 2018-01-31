# coding=utf-8
"""utils package

实现一些业务无关的逻辑 """

from __future__ import absolute_import, division, print_function, with_statement

import os
import re
import sys
import fnmatch
import logging
import doctest
import traceback
import functools
import unicodedata
import urlparse
from importlib import import_module

from tornado.web import RequestHandler
from tornado.escape import utf8, to_unicode

__author__ = "Yihang Yang"
__copyright__ = "Copyright 2015, Kanjian"
__credits__ = ["Yihang Yang"]
__license__ = "Apache"
__version__ = "2.0"
__maintainer__ = "Yihang Yang"
__email__ = "lianghuihui@kanjian.com"
__status__ = "Production"

__all__ = ['load_object', "cached_property", "valid_filename", "ClassProperty", "ControllerLoader", "SingletonMeta",
           "compatible_cmp", "file_clear_contents", "change_url_scheme", "upc_ean_to_barcode", "contain_chinese"]

_MISSING = object()


def load_object(path):
    """Load an object given its absolute object path, and return it.

    object can be a class, function, variable or an instance.
    path ie: 'scrapy.downloadermiddlewares.redirect.RedirectMiddleware'
    """

    try:
        dot = path.rindex('.')
    except ValueError:
        raise ValueError("Error loading object '%s': not a full path" % path)

    module, name = path[:dot], path[dot+1:]
    mod = import_module(module)

    try:
        obj = getattr(mod, name)
    except AttributeError:
        raise NameError("Module '%s' doesn't define any object named '%s'" % (module, name))

    return obj


# pylint: disable=protected-access
class cached_property(property):  # pylint: disable=invalid-name
    """重写property，添加一个缓存机制，使用了_MISSING后，对None值也可以缓存

    设计思路：
    缓存的值写在"_{}".format(attribute_name)里面，
    所有缓存都标记在"_cached_properties"里面。
    想过设计更统一的东东，比如所有缓存的值都写在一个attribute里面，不过似乎写setter的时候会坑
    切忌：除了setter之外，其他代码尽力不要设置"_{}".format(attribute_name)里的值，否则代码会相当confused
    """
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        value = obj.__dict__.get("_{}".format(self.fget.__name__), _MISSING)  # 手动在__dict__里面查找
        if value is _MISSING:
            value = super(cached_property, self).__get__(obj, objtype)  # 找不到就获取值
            obj.__dict__["_{}".format(self.fget.__name__)] = value  # 写入数据
        return value


# pylint: enable=protected-access


class ClassProperty(object):
    """类的属性, 至于带缓存的功能，稍后再议吧

    Reference:
        https://gist.github.com/josiahcarlson/1561563
    """
    def __init__(self, fget, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc

    def __get__(self, obj, objtype=None):
        if self.fget is None:
            raise AttributeError("unreadable class attribute")
        if objtype is None:
            objtype = type(obj)
        return self.fget(objtype)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("unreadable class attribute")
        objtype = type(obj)
        self.fset(objtype, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("unreadable class attribute")
        objtype = type(obj)
        self.fdel(objtype)

    def getter(self, fget):
        """gettter"""
        return ClassProperty(fget, self.fset, self.fdel, self.__doc__)

    def setter(self, fset):
        """setter"""
        return ClassProperty(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        """deleter"""
        return ClassProperty(self.fget, self.fset, fdel, self.__doc__)


class SingletonMeta(type):
    """单例的__metaclass__

    用来实现单例，不知道是否线程安全
    Usage:
        >>> class YouClass(object):
        ...     __metaclass__ = SingletonMeta
        ...
        >>> YouClass() is YouClass()
        True
    """
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls.__instances[cls]


VALID_MODULE_NAME = re.compile(r'[_a-z]\w*\.py$', re.IGNORECASE)


class ControllerLoader(object):  # pylint: disable=too-few-public-methods
    """用于载入所有需要用的controller

    Reference:
        http://hg.python.org/cpython/file/181ced5bf0be/Lib/unittest/loader.py
    """
    __metaclass__ = SingletonMeta

    def __init__(self):
        self._top_level_dir = None

    def discover(self, start_dir, pattern="*", top_level_dir=None, urls_py=None):
        """discover controller from start_dir"""
        if top_level_dir is None:
            top_level_dir = start_dir
        top_level_dir = os.path.abspath(top_level_dir)
        if not top_level_dir in sys.path:
            sys.path.append(top_level_dir)
        self._top_level_dir = top_level_dir

        is_not_importable = False
        if os.path.isdir(os.path.abspath(start_dir)):
            start_dir = os.path.abspath(start_dir)
            if start_dir != top_level_dir:
                is_not_importable = not os.path.isfile(os.path.join(start_dir, '__init__.py'))
        else:
            try:
                __import__(start_dir)
            except ImportError:
                is_not_importable = True
            else:
                the_module = sys.modules[start_dir]
                start_dir = os.path.abspath(os.path.dirname(the_module.__file__))
        if is_not_importable:
            raise ImportError('Start directory is not importable: %r' % start_dir)

        controllers = []
        for _controllers in self._find_controllers(start_dir, pattern):
            controllers.extend(_controllers)

        if urls_py is not None:
            self._print_urls_py(controllers, urls_py)

        return controllers

    @staticmethod
    def _print_urls_py(controllers, urls_py):
        """写一个urls_py，不太健壮的一段代码"""
        with open(urls_py, "w") as f:  # pylint: disable=invalid-name
            f.write("#encoding=utf-8\n")
            f.write("'''\n")
            f.write("Notice the os.path.insert or os.path.append, and the file may fails. It's just a guide.\n")
            f.write("'''\n")
            for controller in controllers:
                uri, obj = controller
                f.write("from {} import {}\n".format(obj.__module__, obj.__name__))
            f.write("\n\n")
            f.write("urls = [\n")
            for controller in controllers:
                uri, obj = controller
                _real_path = sys.modules[obj.__module__].__file__
                import __main__
                _real_path = os.path.relpath(_real_path, __main__.__file__)
                f.write("    (r'{}', {}),  # @file {}\n".format(uri, obj.__name__, _real_path))
            f.write("]\n")

    def _find_controllers(self, start_dir, pattern):  # pylint: disable=too-many-locals
        """在start_dir目录下根据pattern查找controller类"""
        paths = os.listdir(start_dir)
        for path in paths:
            full_path = os.path.join(start_dir, path)  # 当前目录
            if os.path.isfile(full_path):  # 如果是文件，查找文件中的class载入
                if not VALID_MODULE_NAME.match(path):  # 是否为Python文件
                    continue
                if not self._match_path(path, full_path, pattern):
                    continue
                name = self._get_name_from_path(full_path)
                if name == "__init__":
                    continue
                try:
                    module = self._get_module_from_name(name)
                except Exception:  # 类没有正常import，大概需要logging吧 pylint: disable=broad-except
                    logging.warn("Failed to import controller module: %s\n%s", name, traceback.format_exc())
                else:
                    mod_file = os.path.abspath(getattr(module, '__file__', full_path))
                    realpath = os.path.splitext(os.path.realpath(mod_file))[0]
                    fullpath_notetext = os.path.splitext(os.path.realpath(full_path))[0]
                    if realpath.lower() != fullpath_notetext.lower():
                        module_dir = os.path.dirname(realpath)
                        mod_name = os.path.splitext(os.path.basename(full_path))[0]
                        expected_dir = os.path.dirname(full_path)
                        msg = ("%r module incorrectly imported from %r. Expected %r. "
                               "Is this module globally installed?")
                        raise ImportError(msg % (mod_name, module_dir, expected_dir))
                    yield self._load_controllers_from_module(module)
            elif os.path.isdir(full_path):  # 如果是文件夹，迭代进去
                if not os.path.isfile(os.path.join(full_path, '__init__.py')):  # 不是package，不鸟
                    continue
                for controllers in self._find_controllers(full_path, pattern):
                    yield controllers

    @staticmethod
    def _generate_controllers(controller):
        """_generate_controllers"""
        if not issubclass(controller, RequestHandler):
            return {}
        urls = controller.__dict__.get("urls", [])  # 保证urls不是继承来的
        if isinstance(urls, str):
            urls = [urls, ]
        if isinstance(urls, list):
            return [(url, controller) for url in urls if isinstance(url, str)]
        return []

    def _load_controllers_from_module(self, module):
        """返回一个dict，url: RequestHandler"""
        controllers = []
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and issubclass(obj, RequestHandler):
                controllers.extend(self._generate_controllers(obj))
        return controllers

    @staticmethod
    def _match_path(path, full_path, pattern):  # pylint: disable=unused-argument
        """判断path是否满足pattern"""
        return fnmatch.fnmatch(path, pattern)

    def _get_name_from_path(self, path):
        """根据path返回对应的包名"""
        path = os.path.splitext(os.path.normpath(path))[0]

        _real_path = os.path.relpath(path, self._top_level_dir)
        assert not os.path.isabs(_real_path), "Path must be within the project"
        assert not _real_path.startswith('..'), "Path must be within the project"

        name = _real_path.replace(os.path.sep, '.')
        return name

    @staticmethod
    def _get_module_from_name(name):
        """根据name(字符串)返回对应包"""
        __import__(name)
        return sys.modules[name]


def doctests():
    """doctests"""
    return doctest.DocTestSuite()


def file_clear_contents(path):
    """清空文件内容

    但保留Access Time和Modified Time.
    """
    if os.path.exists(path):
        access_time = os.path.getatime(path)
        modified_time = os.path.getmtime(path)
        open(path, "w").close()
        os.utime(path, (access_time, modified_time))


def normalize_NFKD(unistring):  # pylint: disable=invalid-name
    """读入一个unicode，将其中的全角符号转换成半角符号"""
    normalize = functools.partial(unicodedata.normalize, "NFKD")
    return "".join(map(normalize, unistring))  # pylint: disable=bad-builtin


def truncate_filename(filename, keep_extension=True):
    """In Linux, filename can't exceed 256. (EXT4)

    :rtype: unicode
    """
    filename = to_unicode(filename)
    max_length = 200
    if len(filename) > max_length:
        if keep_extension and '.' in filename:
            comps = filename.split('.')
            extension = comps[-1]
            name = ".".join(comps[:-1])[:max_length-1-len(extension)]
            filename = name + "." + extension
        else:
            filename = filename[:max_length]

    return filename


def valid_filename(filename, keep_extension=True):
    """Make filename valid by replacing invalid characters.

    Invalid characters: / * | : " < > ? % \ @
    Full-width symbols will be replaced by half-width symbols.

    :param filename: original filename
    :param keep_extension: keep extension
    :type filename: unicode | str
    :rtype: unicode
    :return: new filename
    """

    filename = to_unicode(filename)
    filename1 = truncate_filename(filename, keep_extension=keep_extension)
    filename2 = re.sub(r'[@/*|:"<>?%\\]', u"_", filename1)
    filename3 = filename2.lstrip().rstrip(u". ")
    filename3 = normalize_NFKD(filename3)
    filename3 = filename3.replace(u"。", u".")
    return filename3


def compatible_cmp(a, b):
    """Compatible cmp() func in python 3

    see: https://docs.python.org/3.0/whatsnew/3.0.html#ordering-comparisons
    """
    return (a > b) - (a < b)


def change_url_scheme(url):
    """把url的http换成https"""
    if not url:
        return ''
    parsed = urlparse.urlparse(url)
    parsed = parsed._replace(scheme='https')
    return urlparse.urlunparse(parsed)


def upc_ean_to_barcode(value):
    if len(value) == 12:
        return upc_to_barcode(value)
    if len(value) == 13:
        return ean_to_barcode(value)
    return ''


def ean_to_barcode(value):
    gug = ["LLLLLL", "LLGLGG", "LLGGLG", "LLGGGL", "LGLLGG", "LGGLLG", "LGGGLL", "LGLGLG", "LGLGGL", "LGGLGL"]
    first = int(value[0])
    enc = "_" + str(first) + "*"
    m = len(value) if len(value) < 7 else 7
    for i in range(1, m):
        enc += gug[first][i-1]+value[i]
    enc += '**'

    m = len(value) if len(value) < 12 else 12
    for i in range(7, m):
        enc += 'R'+value[i]

    pr = 0
    for i in range(min(len(value), 12), 0, -1):
        pr += int(value[i-1])*(1 if i % 2 == 1 else 3)
    pr = (10-(pr % 10)) % 10
    enc += 'R'+str(pr)
    enc += '*'
    return enc


def upc_to_barcode(value):
    """参考 https://www.carolinabarcode.com/upc-barcode-font-primer-a-88.html"""
    l1 = 'QWERTYUIOP'
    l2 = 'ASDFGHJKL;'
    l3 = 'ZXCVBNM,./'
    return value[0] +\
        l1[int(value[1])-1] +\
        l1[int(value[2])-1] +\
        l1[int(value[3])-1] +\
        l1[int(value[4])-1] +\
        l1[int(value[5])-1] +\
        '-' +\
        l2[int(value[6])-1] +\
        l2[int(value[7])-1] +\
        l2[int(value[8])-1] +\
        l2[int(value[9])-1] +\
        l2[int(value[10])-1] +\
        l3[int(value[11])-1]


def contain_chinese(text):
    return any(u'\u4e00' <= c <= u'\u9fff' for c in to_unicode(text))


if __name__ == "__main__":
    filename_0 = "我 * | ? < > % / \\ @"
    print(filename_0)
    print(valid_filename(filename_0))
    print(valid_filename("abcd." * 100 + ".mp3"))
