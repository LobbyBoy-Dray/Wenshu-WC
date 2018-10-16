import os

print('应有数量', '实际数量', '去重后数量', sep = '****')
path = './文书ID'
files = os.listdir(path)
files = files[1:]
for file in files:
	filePath = os.path.join(path, file)
	with open(filePath, encoding = 'utf-8') as f:
		text = [x.strip() for x in f.readlines()]
	shouldbe = text[1]
	actualbe = len(text)-3
	text = set(text)
	text = list(text)
	withdrbe = len(text)-3
	print(shouldbe, actualbe, withdrbe, sep = '****')