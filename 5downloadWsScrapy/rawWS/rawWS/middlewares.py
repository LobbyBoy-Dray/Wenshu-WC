# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals


class RawwsDownloaderMiddleware(object):
    def process_response(self, request, response, spider):
        # 页面是否存在
        if response.status != 200:
            print('******该次访问状态码错误【%d】，【%s】，重试！******' %(response.status, response.url))
            return request
        return response

    def process_exception(self, request, exception, spider):
        print("**********")
        print("错误出现：【%s】" %(str(exception)))
        print("重试！")
        print("**********")
        return request 
