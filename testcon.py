# conversation_store = {
#     'conversation_name': "Nho",
#     "conversation_list": ['Hi how are you doing?', 'I love you', 'Fuck liverppool']
# }

# print(conversation_store['conversation_list'])
# print(conversation_store['conversation_name'])
# conversation_store['Hih'] = 'cc'
# print(conversation_store)

# # print(conversation_store[0])
# bytes_data = b''
# BUFFER_SIZE = 1024 * 4
# filename = "trash_cart_1.png"
# with open(filename, 'rb') as f:
# 	while True:
# 		bytes_read = f.read(BUFFER_SIZE)
# 		if not bytes_read:
# 			f.close()
# 			break
# 		bytes_data += bytes_read

# with open(f'received_{filename}', 'wb') as f:
# 	f.write(bytes_data)

import os

path = os.getcwd()
dir_list = os.listdir(path)
print(dir_list)