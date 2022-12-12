# conversation_store = {
#     'conversation_name': "Nho",
#     "conversation_list": ['Hi how are you doing?', 'I love you', 'Fuck liverppool']
# }

# print(conversation_store['conversation_list'])
# print(conversation_store['conversation_name'])
# conversation_store['Hih'] = 'cc'
# print(conversation_store)

# print(conversation_store[0])

#create a function:
def myfunction():
  global x
  x = "hello"

#execute the function:
myfunction()

#x should now be global, and accessible in the global scope.
x = x + 'hello'
print(x)