from AES_module import AES
from ECC_module import ECC
from Convert import converter
import ast

aes_key = "21"
ecc_private = "123"
ecc_public = ""
C1_aesKey = ""
C2_aesKey = ""
C1_multimedia = ""
C2_multimedia = ""

ecc_private_key= ecc_private
ecc_obj_AESkey = ECC.ECC()
ecc_public_key = ecc_obj_AESkey.gen_pubKey(int(ecc_private_key))
ecc_public = str(ecc_public_key)
print(ecc_public)
print("-------------------------------------------------------------------------")

ecc_obj_AESkey = ECC.ECC()
(C1_aesKey, C2_aesKey) = ecc_obj_AESkey.encryption(ast.literal_eval(ecc_public), str(int(aes_key)))
print(C1_aesKey,C2_aesKey)
print("-------------------------------------------------------------------------")

file = r".\uploads\wp7242561.jpg"
multimedia_data = converter.fileToBase64(str(file))
aes = AES.AES(int(aes_key))
encrypted_multimedia = aes.encryptBigData(multimedia_data)
data_for_ecc = converter.makeSingleString(encrypted_multimedia)
ecc = ECC.ECC()
(C1_multimedia, C2_multimedia) = ecc.encryption(ast.literal_eval(ecc_public), data_for_ecc) 
print(C1_multimedia)
print("C2_multimedia--------------------------------------------")
print(C2_multimedia)
print("-------------------------------------------------------------------------")

# decrypt
file_name = file
ecc_AESkey = ECC.ECC()
decryptedAESkey = ecc_AESkey.decryption(C1_aesKey, C2_aesKey, ecc_private)

ecc_obj = ECC.ECC()
encrypted_multimedia = ecc_obj.decryption(C1_multimedia, C2_multimedia, ecc_private)
clean_data_list = converter.makeListFromString(encrypted_multimedia)

aes_obj = AES.AES(int(decryptedAESkey))
decrypted_multimedia = aes_obj.decryptBigData(clean_data_list)


output_file = r".\downloads\wp7242561.jpg"
converter.base64ToFile(decrypted_multimedia, str(output_file))
