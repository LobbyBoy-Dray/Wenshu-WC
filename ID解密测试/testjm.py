from Crypto.Cipher import AES
import os
import execjs


# Part One: 使用phantom解析得到真正的_KEY
# 必须拿到RunEval
RunEval = "w61aQW7CgzAQfAtRDsK2wqjDugHClFPCnsOQw6PDikIVSRsODcKVQ09Rw75ewqDDlCXDoGJSG8OHaUZCGxnCr3dmw4fDi8KCwqUsd8O5ZnvDiGTDvl7CrsKeSsKZw69fH19kw7HCtsOePcOLdcKxw5nCsjjCiknDgARtHiACw4x9VMOIf0jDpE4eV3Qlw6wtDHTCh8KyMMOYPSjChsONwoUcSBjCmiB1wogAdSAMw7LChxLDiBo6ITnCpMKEHcKAQSEEaHjCksKkwqtFVsOsD8Klw7zDiMOKQi7CksKUUlFdwozDhcOHU8OtwqbCrsOjwonDk8OXSsKqwowQMcKLwpoJTsOnMcOrCcOzTDNcw77DvDvCgVh9wrvDssKgwqjCniFBw5VPD8Oww5w9ahfDvA7DlsOjwq3DtR3DpcOUwo3CpsK/wq/CoBrDlkPCiQYUwrQ5wozDhFYkwqcpw5oZGmlPw7TCuMOEw61iw5/Cvy3CsFhlwrvDlFjDonbCkcOdBcOpF05vw6QWw4fDsBg4woXCmcKDwrpzw5nDncKzw7MuwrECVC1swq7DvGZjw68hwro7wojDgFrCh38cw7fDrWjCtMO3wrXChcO9w73CpTEsecONw4xsT8KZw4PChsOvwpvDvDXDi8OQF8Kiw70HwoNvPcOMwrBXw6LDpAs7w4TCt8O5DXxhw5wMwoHClsOFwqDCq085w40FwqnCl8Omw7BmeGXDqcOvdgPCksOFw7EzIMOxw4DCpwPDixlPPgE="
realKey = os.popen('phantomJS realKey.js %s' % RunEval).read()
realKey = realKey.strip()
print(realKey)

# Part Two: 先将加密的文书ID解包
fakeID = "DcKNwrkBADEIw4NWw6LCucKAKXnDgsO+I10KdcKWZcKYwpFRQHjCsjsPYMOZw7fCqy8bwplVLVfClsKsw7nCqsOKccOSFUXDm8OTwqxiwofCo8OjGnk1wp8NJDrCmEx2bMKPfMOQPsOrZcKdNcKcKsKDfMOsXsKDVcOCw60idMOcMwNUU3zCk8KyTMOJOXDDukjCt8KPUBxEwp3Co8OYwpHCjBklw6HCrE/CrcOmRcKfJ8OcwrJvwpoew77DjsKpVG5+HcKwHw=="
fp = open('unzipp.js')
js = fp.read()
ct = execjs.compile(js)
encrypted_doc_id = ct.call('unzip',fakeID)
print(encrypted_doc_id)

# Part Three: 解密解包后的文书ID
pkcs7 = {
    'padding': lambda bs: bs + bytes(
        [AES.block_size - len(bs) % AES.block_size] * (AES.block_size - len(bs) % AES.block_size)),
    'unpadding': lambda bs: bs[:-bs[-1]]
}
key = bytes(realKey, 'utf8')
iv = b'abcd134556abcedf'
mode = AES.MODE_CBC
aes = AES.new(key, mode, iv)
def decrypt_inner(ciphertxt):
    aes = AES.new(key, mode, iv)
    return pkcs7['unpadding'](aes.decrypt(bytes.fromhex(ciphertxt)))
d1 = decrypt_inner(encrypted_doc_id).decode()
print(d1)
d2 = decrypt_inner(d1)
print(d2)

