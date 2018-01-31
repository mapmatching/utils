# coding=utf-8
"""Tornado的middleware package

但是业务无关
"""
from __future__ import absolute_import, division, print_function, with_statement

import itertools

from tornado.log import access_log


__all__ = ["LogMiddleware"]


# pylint: disable=no-member
# pylint: disable=too-few-public-methods
class LogMiddleware(object):
    """LOG的middleware"""

    def _log(self):
        """重写log方式

        虽然在这里写是不太推荐，不过比较容易复用
        response的body虽然也可以用一些hack的方法取到，但比较破坏整个tornado的结构，以后再说，大概可以用transform来搞定

        copy from `tornado.web.Application.log_request`
        """
        if self.get_status() < 400:
            log_method = access_log.info
        elif self.get_status() < 500:
            log_method = access_log.warning
        else:
            log_method = access_log.error

        itertools.chain(*self.request.files.values())

        request_time = 1000.0 * self.request.request_time()

        log_method(repr(self.request_data))
        log_method("%d %s %.2fms", self.get_status(), self._request_summary(), request_time)

    @property
    def request_data(self):
        """请求的数据"""
        return dict(
            arguments=self.request.arguments, # 参数,类型dict
            headers=self.request.headers, # 头,类型HTTPHeader,类似于dict
            url=self.request.full_url(), # url,类型HTTPFile,类似于dict
            files=[{"filename": request_file.filename, "content_type": request_file.content_type,
                    "body_length": len(request_file.body)} for request_file in
                   itertools.chain(*self.request.files.values())], # 文件meta信息
            response_headers=self._headers, # response的headers,类似于dict
        )
