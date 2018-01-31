# coding=utf-8
"""runtime context package
"""
from __future__ import absolute_import, division, print_function, with_statement

import weakref

# 理论上来说，下面这段代码应该写在`tools/locale.py`里
from tornado.locale import Locale, load_gettext_translations, set_default_locale

import settings
from tools import get_session_class, connection

load_gettext_translations(settings.TRANSLATIONS_DIRECTORY, settings.TRANSLATIONS_DOMAIN)
set_default_locale(settings.DEFAULT_LOCALE)


__author__ = "Chuanchuan Tu"
__copyright__ = "Copyright 2016, Kanjian"
__credits__ = ["Chuanchuan Tu"]
__license__ = "Apache"
__version__ = "2.0"
__maintainer__ = "Chuanchuan Tu"
__email__ = "tuchuanchuan@kanjian.com"
__status__ = "Production"

__all__ = ["RuntimeContext"]


class RuntimeContext(object):
    """运行时上下文

    目前包含以下内容：
    orm_session：sqlalchemy的session，用于读取数据库
    locale：当前locale信息，用于翻译
    """
    def __init__(self, orm_session, locale=None, cache=None):
        """Initializer

        :type orm_session: sqlalchemy.orm.Session
        :type locale: tornado.locale.Locale
        :type cache: redis.Redis
        """
        self.orm_session = orm_session
        self.cached_dict = weakref.WeakValueDictionary()  # used for orm cache
        if locale is None:
            self.locale = Locale.get_closest("zh_CN")
        else:
            self.locale = locale
        self.cache = cache  # redis cache


def get_context(db_name="default"):
    """Get RuntimeContext object, defaults pointing to `default` database.

    :rtype: RuntimeContext
    """
    session = get_session_class(bind=connection[db_name])(autoflush=False)
    context = RuntimeContext(orm_session=session)
    return context
