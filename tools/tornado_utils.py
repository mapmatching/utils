# coding=utf-8
"""tornado_utils package

"""
from __future__ import absolute_import, division, print_function, with_statement

import json
import functools

from tornado import httputil
from tornado.web import HTTPError, MissingArgumentError


__author__ = "Yihang Yang"
__copyright__ = "Copyright 2015, Kanjian"
__credits__ = ["Yihang Yang"]
__license__ = "Apache"
__version__ = "2.0"
__maintainer__ = "Yihang Yang"
__email__ = "lianghuihui@kanjian.com"
__status__ = "Production"


__all__ = ['para', 'para_file', 'KanjianHTTPError']

# pylint: disable=missing-docstring
# pylint: disable=too-few-public-methods

_missing = object()  # pylint: disable=invalid-name


def para(name, strip=True, required=True, validator=None, status_code=400, response_body=None):  # pylint: disable=too-many-arguments
    """用于Tornado.web.RequestHandler做基本的类型检查

    如果存在异常，在抛出KanjianHTTPError, 包含status_code并且渲染response_body
    """
    def decorator(get_or_post):
        @functools.wraps(get_or_post)
        def wrapper(self, *args, **kwargs):
            # 检查参数
            try:
                argument = self.get_argument(name, strip=strip)
                if argument is None and required:
                    raise HTTPError(status_code)
            except HTTPError as error:
                if isinstance(error, MissingArgumentError) and not required:
                    # 如果是MissingArgumentError并且不是required, 放它一马
                    # 这个判断语句不用else的话略confuse
                    argument = _missing
                else:
                    if status_code != 400 or response_body != None:  # 定制化返回结果
                        kanjian_httperror = KanjianHTTPError.from_httperror(
                            error, status_code=status_code, response_body=response_body)
                        raise kanjian_httperror
                    else:
                        raise error
            if not argument is _missing and validator:  # 存在validator的话，验证一下
                if not validator(argument):
                    raise KanjianHTTPError(
                        status_code, 'Argument %s is not valid' % name, response_body=response_body)
            return get_or_post(self, *args, **kwargs)
        return wrapper
    return decorator


def para_file(name, name_old=None, required=True, status_code=400, response_body=None):
    """用于Tornado.web.RequestHandler做基本的类型检查

    如果存在异常，在抛出KanjianHTTPError, 包含status_code并且渲染response_body
    """
    def decorator(get_or_post):
        @functools.wraps(get_or_post)
        def wrapper(self, *args, **kwargs):
            if name_old is not None:
                file_old = self.get_argument(name_old, None)
            else:
                file_old = None
            try:
                argument = self.request.files.get(name)
                if not argument and not file_old:
                    raise MissingArgumentError(name)
            except HTTPError as error:
                if isinstance(error, MissingArgumentError) and not required:
                    argument = _missing
                else:
                    if status_code != 400 or response_body != None:  # 定制返回结果
                        kanjian_httperror = KanjianHTTPError.from_httperror(
                            error, status_code=status_code, response_body=response_body)
                        raise kanjian_httperror
                    else:
                        raise error
            return get_or_post(self, *args, **kwargs)
        return wrapper
    return decorator


class KanjianHTTPError(HTTPError):

    """基本参考了tornado.web.HTTPError，做了一些adaptor"""

    def __init__(self, status_code, log_message=None, *args, **kwargs):  # pylint: disable=super-init-not-called
        """多取一个参数response_body"""
        self.status_code = status_code
        self.log_message = log_message
        self.args = args
        self.reason = kwargs.get('reason', None)
        self.response_dict = kwargs.get('response_dict', None)
        self.response_body = kwargs.get('response_body', None)

    def __str__(self):
        """多存在response_body的话，则调用它返回所需要的body"""
        message = "HTTP %d: %s" % (
            self.status_code,
            self.reason or httputil.responses.get(self.status_code, 'Unknown'))
        if self.log_message:
            body = message + " (" + (self.log_message % self.args) + ")"
        else:
            body = message

        if self.response_body:  # 如果存在response_body，则调用之
            return self.response_body(body)
        elif self.response_dict:
            return json.dumps(self.response_dict)
        else:
            return body

    @classmethod
    def from_httperror(cls, http_error, status_code=None, response_dict=None, response_body=None):
        """tornado.web.HTTPError转成KanjianHTTPError"""
        return cls(
            status_code or http_error.status_code,
            http_error.log_message,
            response_dict=response_dict,
            response_body=response_body,
            reason=http_error.reason,
            *http_error.args)


class ResponseBody(object):
    """ResponseBody接口类，实际上啥都不干，需要被override"""

    def __init__(self, *args, **kwargs):
        """一般来说会override"""
        raise NotImplementedError()

    def __call__(self, body):
        """一般来说会override"""
        raise NotImplementedError()


class JsonResponseBoby(ResponseBody):

    """定义一种我们常用的json返回类型"""
    def __init__(self, error_code=1024, default_message=None):  # pylint: disable=super-init-not-called
        self.error_code = error_code
        self.default_message = default_message

    def __call__(self, body):
        """json dumps一下要返回的json包，如果要返回更复杂形式的json包，联系Goat"""
        return json.dumps(dict(ret=self.error_code, msg=self.default_message or body))
