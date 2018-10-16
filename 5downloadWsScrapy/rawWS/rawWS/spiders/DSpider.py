# -*- coding: utf-8 -*-
import scrapy


class DspiderSpider(scrapy.Spider):
	name            = 'DSpider'
	allowed_domains = ['wenshu.court.gov.cn']
	wsIdFilePath    = '../../文书ID(去重)/WSID.txt'
	rawFilePath     = '../../目标文书(原始已去重)/'
	headers = {
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
		'Accept-Encoding':'gzip, deflate',
		'Accept-Language':'zh-CN,zh;q=0.9',
		'Cache-Control':'max-age=0',
		'Connection':'keep-alive',
		'Host':'wenshu.court.gov.cn',
		'Upgrade-Insecure-Requests':'1',
		'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
	}


	def start_requests(self):
		with open(self.wsIdFilePath) as f:
			WSIDs = [x.strip() for x in f.readlines()]
		for WSID in WSIDs:
			url = "http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID=%s" %(WSID)
			yield scrapy.Request(url, headers = self.headers, callback = self.parseAllText, meta = {'WSID':WSID}, dont_filter = True)


	def parseAllText(self, response):
		WSID = response.meta['WSID']
		text = response.text
		if ('HtmlNotExist' in text) or ('remind key' in text) or (text == ''):
			print('!!!出现三种错误之一!!!')
			url = "http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID=%s" %(WSID)
			yield scrapy.Request(url, headers = self.headers, callback = self.parseAllText, meta = {'WSID':WSID}, dont_filter = True)
		else:
			with open(self.rawFilePath + '%s.txt' % WSID, 'w', encoding = 'utf8') as f:
				f.write(text)
			print('完成一条')


