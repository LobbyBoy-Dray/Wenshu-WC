# coding=utf-8
import requests
import execjs
import json
import io
import sys
import re
import time
from urllib import parse

class cpwsSpider:
	codeUrl = "http://wenshu.court.gov.cn/ValiCode/GetCode"
	listContentsUrl = "http://wenshu.court.gov.cn/List/ListContent"
	headers_for_number = {
		'Host':'wenshu.court.gov.cn',
		'Origin':'http://wenshu.court.gov.cn',
		'Referer':'http://wenshu.court.gov.cn/',
		'X-Requested-With':'XMLHttpRequest',
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
	}
	headers_for_vjkl5 = {
		"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
		"Accept-Encoding":"gzip, deflate",
		"Accept-Language":"zh-CN,zh;q=0.8",
		"Host":"wenshu.court.gov.cn",
		"Proxy-Connection":"keep-alive",
		"Upgrade-Insecure-Requests":"1",
		"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36"
	}
	headers_for_listContents = {
		"Accept":"*/*",
		"Accept-Encoding":"gzip, deflate",
		"Accept-Language":"zh-CN,zh;q=0.8",
		"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
		"Host":"wenshu.court.gov.cn",
		"Origin":"http://wenshu.court.gov.cn",
		"Proxy-Connection":"keep-alive",
		"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
		"X-Requested-With":"XMLHttpRequest"
	}

	Param = ""
	count = 0
	Page = 20
	Order = "裁判日期"
	Direction = "desc"							# asc正序，desc倒序

	counter = 0

	def __init__(self, filename):
		self.filename = filename
		with open('./文书ID/%s.txt' % filename, encoding = 'utf-8') as f:
			baseInfo = [x.strip() for x in f.readlines()]
		self.Param = baseInfo[0]
		self.count = int(baseInfo[1])
		session = requests.Session()
		self.session = session
		sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')		#改变标准输出的默认编码

	# 获取页数
	def getPageTo(self):
		count = int(self.count)
		pageTo = count//20+1 if count%20 != 0 else count//20
		return pageTo

	# 获取guid参数
	def get_guid(self):
		js1 = '''
			function getGuid() {
				var guid = createGuid() + createGuid() + "-" + createGuid() + "-" + createGuid() + createGuid() + "-" + createGuid() + createGuid() + createGuid(); //CreateGuid();
				return guid;
			}
			var createGuid = function () {
				return (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1);
			}
		'''
		ctx1 = execjs.compile(js1)
		guid = (ctx1.call("getGuid"))
		return guid

	# 根据guid获取number
	def get_number(self, guid):
		session = self.session
		url = self.codeUrl
		headers = self.headers_for_number
		data = {'guid':guid}
		r = session.post(url, data = data, headers = headers)
		statuscode = r.status_code
		while statuscode != 200:
			print('503出现，正在重试')
			return self.get_number(guid)
		number = r.text
		return number

	# 根据number和guid获取cookie中的vjkl5
	def get_vjkl5(self, guid, number):
		session = self.session
		url = "http://wenshu.court.gov.cn/list/list/?sorttype=1&number=" + number + "&guid=" + guid + "&conditions=searchWord+QWJS+++" + parse.quote(self.Param)
		headers = self.headers_for_vjkl5
		try:
			r = session.get(url, headers = headers, timeout = 10)
		except:
			return self.get_vjkl5(guid, number)
		statuscode = r.status_code
		while statuscode != 200:
			print('503出现，正在重试')
			return self.get_vjkl5(guid, number)
		vjkl5 = r.cookies["vjkl5"]
		return vjkl5


	# 根据vjkl5获取参数vl5x
	def get_vl5x(self, vjkl5):
		with open('./JS文件/getkey.js') as fp:
			js = fp.read()
			ctx = execjs.compile(js)
			vl5x = (ctx.call('getKey',vjkl5))
		return vl5x



	# 根据-第几页-获取数据
	def get_data(self, Index):
		session = self.session
		guid = self.get_guid()
		number = self.get_number(guid)
		vjkl5 = self.get_vjkl5(guid, number)
		vl5x = self.get_vl5x(vjkl5)
		url = self.listContentsUrl
		headers = self.headers_for_listContents
		data = {
			"Param":self.Param,
			"Index":Index,
			"Page":self.Page,
			"Order":self.Order,
			"Direction":self.Direction,
			"vl5x":vl5x,
			"number":number,
			"guid":guid
		}
		try:
			r = session.post(url, headers = headers, params = data)
		except:
			return self.get_data(Index)
		statuscode = r.status_code
		while statuscode != 200:
			print('503出现，正在重试')
			return self.get_data(Index)
		r.encoding = 'utf8'
		text = r.text
		text = text.strip()
		text = text[1:-1]
		text = text.replace(r'\"', r'"')
		text = text.replace(r'\\', '\\')
		try:
			datas = json.loads(text)
			if datas == []:
				print('空了')
				return self.get_data(Index)
			else:
				return datas
		except:
			print('remindkey了')
			return self.get_data(Index)

	def main(self):
		pageTo = self.getPageTo()
		print('共%s页' % str(pageTo))
		for index in range(1, pageTo + 1):
			data = self.get_data(index)
			datas = data[1:]
			print('进入第%s页' % str(index))
			for d in datas:
				WSID = d.get('文书ID')
				with open('./文书ID/%s.txt' % self.filename, 'a', encoding = 'utf-8') as f:
					f.write(WSID)
					f.write('\n')
				self.counter += 1
				print('已抓取第%d个文书ID' % self.counter)
			time.sleep(2)


####################################   执行   #############################################
filename = "案件名称_公司_当事人_美国"

Spider1 = cpwsSpider(filename)
Spider1.main()