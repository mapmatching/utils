# coding=utf-8
"""db package

include:
    SQLAlchemy -> sqlalchemy
    Redis -> redis
    Fastdfs -> fastdfs
"""
# TODO
# Mongodb -> mongodb

from __future__ import absolute_import, division, with_statement

__author__ = "Yihang Yang"
__copyright__ = "Copyright 2015, Kanjian"
__credits__ = ["Yihang Yang"]
__license__ = "Apache"
__version__ = "2.0"
__maintainer__ = "Yihang Yang"
__email__ = "lianghuihui@kanjian.com"
__status__ = "Production"

import logging

import redis
import fdfs_client.client
from tornado.util import import_object
from sqlalchemy import create_engine, event, exc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import Pool


__all__ = ['connection', 'get_session_class']


logging.getLogger("sqlalchemy").propagate = False
# pylint: disable=too-few-public-methods


class _ConnectionHandler(object):
    """_ConnectionHandler

    copy from django
    """

    def __init__(self, databases=None):
        """
        databases is an optional dictionary of database definitions (structured
        like settings.DATABASES).
        """
        if databases:
            self.databases = databases
        else:
            import settings
            self.databases = settings.DATABASES
        self._connections = {}

    def __getitem__(self, alias):
        if alias not in self._connections:
            # NOTE remove _read or _write, 感觉alias_original = alias[:-5]这个写法不是很可读
            if alias.endswith("_read"):
                alias_original = alias[:-5]
            elif alias.endswith("_write"):
                alias_original = alias[:-6]
            else:
                alias_original = alias

            db_config = self.databases[alias_original]
            backend = import_object(db_config["ENGINE"])

            write_conn, read_conn = backend.database_wrapper(db_config, alias_original)

            self._connections.update({
                alias_original: write_conn,
                alias_original + "_write": write_conn,
                alias_original + "_read": read_conn,
            })

        return self._connections[alias]

    def __setitem__(self, key, value):
        setattr(self._connections, key, value)

    def __delitem__(self, key):
        delattr(self._connections, key)

    def __iter__(self):
        return iter(self.databases)


# NOTE this connection must be used with settings
connection = _ConnectionHandler()  # pylint: disable=invalid-name


class _BackendBase(object):
    """_BackendBase"""

    _DEFAULT_PARAMETER = {}

    @classmethod
    def database_wrapper(cls, db_config, alias):
        """database wrapper

        @type db_config: dict "like settings.databases"
        @type alias: string "connection alias"
        """
        return cls._database_wrapper(cls._ensure_config(db_config), alias)

    @classmethod
    def _ensure_default(cls, db_config):
        """add default parameters"""
        tmp_config = cls._DEFAULT_PARAMETER.copy()
        tmp_config.update(db_config)

        return tmp_config

    @classmethod
    def _ensure_config(cls, db_config):
        """ensure config

        配置文件读写分离
        """
        tmp_config = db_config.copy()

        if "write" in tmp_config and "read" in tmp_config:  # 读写分离
            write_config = tmp_config["write"]
            write_config.update(tmp_config)
            del write_config["write"]
            del write_config["read"]

            read_config = tmp_config["read"]
            read_config.update(tmp_config)
            del read_config["write"]
            del read_config["read"]

            return cls._ensure_default(write_config), cls._ensure_default(read_config)
        else:
            return cls._ensure_default(tmp_config), None

    @classmethod
    def _database_wrapper(cls, db_config, alias):  # pylint: disable=unused-argument
        """database wrapper"""
        write_config, read_config = db_config

        write_conn = cls._database_wrapper_single(write_config)
        if read_config:
            read_conn = cls._database_wrapper_single(read_config)
        else:
            read_conn = write_conn

        return write_conn, read_conn

    @classmethod
    def _database_wrapper_single(cls, db_config):
        """database wrapper single"""
        raise NotImplementedError()


class SQLAlchemy(_BackendBase):
    """SQLAlchemy backend"""

    _DEFAULT_PARAMETER = {
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': 3306,
        'DB': 'test',
        'OPTIONS': 'charset=utf8&use_unicode=0',
        'DEBUG': False,
    }

    @staticmethod
    def ping_connection(dbapi_connection, connection_record, connection_proxy):
        """检测mysql连接状态"""
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("SELECT 1")
        except exc.OperationalError, ex:
            import logging
            logging.warn("", exc_info=True)
            if ex.args[0] in (2006,  # MySQL server has gone away
                              2013,  # Lost connection to MySQL server during query
                              2055,  # Lost connection to MySQL server at '%s', system error: %d
                              ):
                raise exc.DisconnectionError()
            else:
                raise
        cursor.close()

    @classmethod
    def _database_wrapper_single(cls, db_config):
        connector = 'mysqldb'

        url = "mysql+{connector}://{USER}:{PASSWORD}@{HOST}/{DB}?{OPTIONS}".format(
            connector=connector, **db_config)

        logging.debug("connect to SQLAlchemy: %s", url)

        engine = create_engine(
            url,
            echo=db_config["DEBUG"],
            echo_pool=True,
            pool_recycle=3600
        )
        event.listen(engine, "checkout", cls.ping_connection)
        return engine


class Redis(_BackendBase):
    """Redis backend"""

    _DEFAULT_PARAMETER = {
        'HOST': '127.0.0.1',
        'PORT': 6379,
        'DB': 0,
        'PASSWORD': None,
    }

    @classmethod
    def _database_wrapper_single(cls, db_config):
        logging.debug("GET redis %s", db_config)
        return redis.Redis(
            connection_pool=redis.ConnectionPool(
                host=db_config['HOST'],
                port=db_config['PORT'],
                db=db_config['DB'],
                password=db_config['PASSWORD'],
            )
        )


class FastDFS(_BackendBase):
    """FastDFS backend"""

    _DEFAULT_PARAMETER = {
        'CONFIG_PATH': "/etc/fdfs/client.conf",
    }

    @classmethod
    def _database_wrapper_single(cls, db_config):
        logging.debug("GET FastDFS %s", db_config)
        return fdfs_client.client.Fdfs_client(conf_path=db_config["CONFIG_PATH"])


_SESSION = {}


def get_session_class(bind):
    """get orm session class (a SQLAlchemy session maker)"""
    global _SESSION  # pylint: disable=global-statement
    if bind not in _SESSION:
        logging.debug("make _SESSION %s", bind)
        _SESSION[bind] = sessionmaker(bind=bind)
    return _SESSION[bind]


class SQLite(_BackendBase):
    """SQLite backend"""

    _DEFAULT_PARAMETER = {
        'DB': '/path/to/db',
        'DEBUG': False,
    }

    @classmethod
    def _database_wrapper_single(cls, db_config):
        logging.debug("GET sqlite sqlite:///{DB}".format(**db_config))  # pylint: disable=logging-format-interpolation
        engine = create_engine(
            "sqlite:///{DB}".format(**db_config),
            echo=db_config["DEBUG"],
            echo_pool=True,
            pool_recycle=3600
        )
        return engine
