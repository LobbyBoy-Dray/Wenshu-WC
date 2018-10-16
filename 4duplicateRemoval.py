import os

allWsId = []
path = './文书ID'
files = os.listdir(path)
files = files[1:]
for file in files:
	filePath = os.path.join(path, file)
	with open(filePath, encoding = 'utf-8') as f:
		text = [x.strip() for x in f.readlines()]
	if len(text) == 3:
		continue
	else:
		text = text[3:]
		allWsId += text

allWsId = set(allWsId)
allWsId = list(allWsId)
print(len(allWsId))

# for each in allWsId:
# 	with open('./文书ID(去重)/WSID.txt', 'a', encoding = 'utf-8') as f:
# 		f.write(each)
# 		f.write('\n')

# with open('./文书ID(去重)/WSID.txt', encoding = 'utf-8') as f:
# 	data = f.readlines()

# print(len(data))