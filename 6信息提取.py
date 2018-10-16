import re
import json
import time
import pymongo
import os



class dealText:
	db_name = "CPWS"
	coll_name = "BaseInfo"
	host = "127.0.0.1"
	port = 27017
	WSpath = './目标文书(原始已去重)'

	def __init__(self):
		files = os.listdir(self.WSpath)
		files = files[1:]
		self.WSFiles = files
		self.counter = 0

	# 全角转半角——太慢了，尽量不用
	def strQ2B(self, ustring):
		ss = []
		for s in ustring:
			rstring = ""
			for uchar in s:
				inside_code = ord(uchar)
				if inside_code == 12288:
					inside_code = 32
				elif (inside_code >= 65281 and inside_code <= 65374):
					inside_code -= 65248
				rstring += chr(inside_code)
			ss.append(rstring)
			result = ""
			for each in ss:
				result += each
		return result

	# 读取raw内容
	def readFromTxt(self, filename):
		with open(filename, encoding = 'utf-8') as f:
			text = f.read()
		return text

	# 获得字典形式的case基本信息
	def getCaseInfo(self, text):
		pattern = re.compile(r'var caseinfo=JSON\.stringify\(({.*?})\);')
		result = pattern.search(text)
		assert result, '没有caseInfo, 出错, %s' %text
		caseInfo = json.loads(result.group(1))
		return caseInfo

	# 获得案件类型
	def getCaseType(self, text):
		pattern = re.compile(r'{ name: "案件类型", key: "caseType", value: "(.*?)" }')
		result = pattern.search(text)
		if result:
			return result.group(1)
		else:
			return None

	# 获得案由
	def getCaseReason(self, text):
		pattern = re.compile(r'{ name: "案由", key: "reason", value: "(.*?)" }')
		result = pattern.search(text)
		if result:
			return result.group(1)
		else:
			return None

	# 获得裁判日期
	def getTrialDate(self, text):
		pattern = re.compile(r'{ name: "裁判日期", key: "trialDate", value: "(.*?)" }')
		result = pattern.search(text)
		if result:
			return result.group(1)
		else:
			return None

	# 获得当事人
	def getAppellor(self, text):
		pattern = re.compile(r'{ name: "当事人", key: "appellor", value: "(.*?)" }')
		result = pattern.search(text)
		if result:
			return result.group(1)
		else:
			return None

	# 获得发布时间
	def getPubTime(self, text):
		pattern = re.compile(r'\\"PubDate\\":\\"(.*?)\\"')
		result = pattern.search(text)
		if result:
			return result.group(1).strip()
		else:
			return None

	def replaceSome(self, dd):
		dd = dd.replace('（', '(')
		dd = dd.replace('）', ')')
		dd = dd.replace('，', ',')
		dd = dd.replace('；', ';')
		dd = dd.replace('：', ':')
		dd = dd.replace('Ｘ', 'X')
		dd = dd.replace('ｘ', 'x')
		dd = dd.replace('［', '[')
		dd = dd.replace('］', ']')
		dd = dd.replace('\n', '')
		return dd

	# 获得文书内容
	def getPureText(self, text):
		pattern = re.compile(r'\\"Html\\":\\"(.*?)\\"\}";')
		result = pattern.search(text)
		html = result.group(1)
		dr = re.compile(r'<[^>]+>', re.S)
		dd = dr.sub('',html)
		if dd:
			dd = self.replaceSome(dd)
		else:
			dd = ''
		return dd

	# 获得文书标题
	def getTitle(self, PureText, CaseNumber):
		if CaseNumber:
			CaseNumber = CaseNumber.replace('(', '\(')
			CaseNumber = CaseNumber.replace(')', '\)')
			pattern = re.compile(r'(.*?)' + CaseNumber)
			result = pattern.search(PureText)
			if result:
				Title = result.group(1).replace(' ','').replace('	','')
				Title = Title.strip()
				Title = Title.replace('文书内容', '', 1)
				return Title
			else:
				return None
		else:
			return None

	# 被告、被告人、被上诉人、被申请人、被执行人
	def judgeBG(self, NA,TEXT):
		# 被告:ABC           OK
		# 被告,ABC           OK
		# 被告ABC            OK
		# 被告(xxx):ABC      OK
		# 被告(xxx),ABC      OK
		# 被告(xxx)ABC       OK
		NA = NA.replace('(', '\(')
		NA = NA.replace(')', '\)')
		NA = NA.replace('[', '\[')
		NA = NA.replace(']', '\]')
		form1 = re.compile('被告:*,*%s' % NA)
		form2 = re.compile('被告\\([^\\)]+\\):*,*%s' % NA)
		form3 = re.compile('被告人:*,*%s' % NA)
		form4 = re.compile('被告人\\([^\\)]+\\):*,*%s' % NA)
		form5 = re.compile('被上诉人:*,*%s' % NA)
		form6 = re.compile('被上诉人\\([^\\)]+\\):*,*%s' % NA)
		form7 = re.compile('被申请人:*,*%s' % NA)
		form8 = re.compile('被申请人\\([^\\)]+\\):*,*%s' % NA)
		form9 = re.compile('被执行人:*,*%s' % NA)
		form10 = re.compile('被执行人\\([^\\)]+\\):*,*%s' % NA)
		form11 = re.compile('被申诉人:*,*%s' % NA)
		form12 = re.compile('被申诉人\\([^\\)]+\\):*,*%s' % NA)
		# form11 = re.compile('原审被告:%s' % NA)
		# form12 = re.compile('原审被告,%s' % NA)
		judge1 = form1.search(TEXT)
		judge2 = form2.search(TEXT)
		judge3 = form3.search(TEXT)
		judge4 = form4.search(TEXT)
		judge5 = form5.search(TEXT)
		judge6 = form6.search(TEXT)
		judge7 = form7.search(TEXT)
		judge8 = form8.search(TEXT)
		judge9 = form9.search(TEXT)
		judge10 = form10.search(TEXT)
		judge11 = form11.search(TEXT)
		judge12 = form12.search(TEXT)
		result = judge1 or judge2 or judge3 or judge4 or judge5 or judge6 or judge7 or judge8 or judge9 or judge10 or judge11 or judge12
		return result

	# 第三人
	def judgeDSR(self, NA,TEXT):
		# 第三人:ABC           OK
		# 第三人,ABC           OK
		NA = NA.replace('(', '\(')
		NA = NA.replace(')', '\)')
		NA = NA.replace('[', '\[')
		NA = NA.replace(']', '\]')
		form1 = re.compile('第三人:*,*%s' % NA)
		form2 = re.compile('第三人\\([^\\)]+\\):*,*%s' % NA)
		judge1 = form1.search(TEXT)
		judge2 = form2.search(TEXT)
		result = judge1 or judge2
		return result

	def getAllInfo(self, text):
		caseInfo = self.getCaseInfo(text)
		CourtID         = caseInfo['法院ID']						# 法院ID
		CourtProceeding = caseInfo['审判程序']					# 审判程序
		CaseNumber      = self.strQ2B(caseInfo['案号']) if caseInfo['案号'] else None			# 案号——可能没有
		CourtName       = caseInfo['法院名称']					# 法院名称
		CourtProvince   = caseInfo['法院省份']					# 法院省份
		CourtCity       = caseInfo['法院地市']					# 法院地市
		CourtDistrict   = caseInfo['法院区县']					# 法院区县
		CourtArea       = caseInfo['法院区域']					# 法院区域
		WSID            = caseInfo['文书ID']			      		# 文书ID
		WSName          = self.strQ2B(caseInfo['案件名称'])		# 文书名称(案件名称)
		CaseType        = self.getCaseType(text)                # 案件类型
		CaseReason      = self.getCaseReason(text)              # 案由
		TrialDate       = self.getTrialDate(text)               # 裁判日期
		Appellor        = self.getAppellor(text)
		if Appellor:
			Appellor    = self.strQ2B(Appellor)                 # 当事人
		else:
			Appellor    = None	
		PubTime         = self.getPubTime(text)                 # 发布时间
		PureText        = self.getPureText(text)				# 文书内容
		# 获取诉讼记录段原文
		SSJLDWY = caseInfo['诉讼记录段原文']			      		# 诉讼记录段原文
		if PureText:
			Title           = self.getTitle(PureText,CaseNumber)	# 文书标题
			Plaintiff  = []											# 原告
			Defendant  = []											# 被告
			Thirdparty = []											# 第三人
			if Appellor:
				Appellor = Appellor.split(',')
				if SSJLDWY:											# 如果有诉讼段原文
					# 分割后搜第一部分
					SSJLDWY = self.strQ2B(SSJLDWY)
					judgeFrom = PureText.split(SSJLDWY[:50])[0]
				else:
					judgeFrom = PureText 							# 如果没有的话，就搜全文吧
				for each in Appellor:
					isBG  = self.judgeBG(each, judgeFrom)
					isDSR = self.judgeDSR(each, judgeFrom)
					if isBG:
						Defendant.append(each)
					elif isDSR:
						Thirdparty.append(each)
					else:
						Plaintiff.append(each)
			if Plaintiff:
				Plaintiff = ','.join(Plaintiff)
			else:
				Plaintiff = None
			if Defendant:
				Defendant = ','.join(Defendant)
			else:
				Defendant = None
			if Thirdparty:
				Thirdparty = ','.join(Thirdparty)
			else:
				Thirdparty = None
		else:
			Title      = None
			Thirdparty = None
			Plaintiff  = None
			Defendant  = None
		if Plaintiff == None and Defendant != None:
			Remarks = 1
		elif Plaintiff != None and Defendant == None:
			Remarks = 2
		elif Plaintiff == None and Defendant == None:
			Remarks = 3
		else:
			Remarks = 0
		# 信息整合
		allInfo = {}
		allInfo['WSID'] 			= WSID
		allInfo['Title']            = Title           if Title           else None
		allInfo['WSName']           = WSName          if WSName          else None
		allInfo['CaseNumber']       = CaseNumber      if CaseNumber      else None
		allInfo['CourtProceeding']  = CourtProceeding if CourtProceeding else None
		allInfo['CaseType']         = CaseType        if CaseType        else None
		allInfo['CaseReason']       = CaseReason      if CaseReason      else None
		allInfo['TrialDate']        = TrialDate       if TrialDate       else None
		allInfo['PubTime']          = PubTime         if PubTime         else None
		allInfo['CourtID']          = CourtID         if CourtID         else None
		allInfo['CourtName']        = CourtName       if CourtName       else None
		allInfo['CourtProvince']    = CourtProvince   if CourtProvince   else None
		allInfo['CourtCity']        = CourtCity       if CourtCity       else None
		allInfo['CourtDistrict']    = CourtDistrict   if CourtDistrict   else None
		allInfo['CourtArea'] 		= CourtArea       if CourtArea       else None
		allInfo['Plaintiff']        = Plaintiff
		allInfo['Defendant']        = Defendant
		allInfo['Thirdparty']       = Thirdparty
		allInfo['Remarks']          = Remarks
		return allInfo

	def convey(self, insertDict):
		conn = pymongo.MongoClient(host = self.host, port = self.port)
		db = conn.get_database(self.db_name)
		coll = db.get_collection(self.coll_name)
		result = coll.insert_one(insertDict)

	def main(self):
		for each in self.WSFiles:
			filePath = './目标文书(原始已去重)/' + each
			text     = self.readFromTxt(filePath)
			allInfo  = self.getAllInfo(text)
			PureText = self.getPureText(text)
			self.convey(allInfo)
			filename = allInfo['CaseNumber'] if allInfo['CaseNumber'] else allInfo['WSID']
			with open('./目标文书(处理已去重)/%s.txt' % filename, 'w', encoding = 'utf-8') as f:
				f.write(PureText)
			self.counter += 1
			print("已处理%s条" % str(self.counter))

###################################################
dealer = dealText()
dealer.main()







