def add_new_user(user):
    with open(r'user_list.txt', 'a+') as file:
        file.writelines(user + '\n')


def check_existence(user):
    found = False
    with open(r'user_list.txt', 'r') as file:
        lines = file.readlines()
        for line in lines:
        # check if string present on a current line
            if line.find(user) != -1:
                print(user, 'string exists in file')
                print('Line Number:', lines.index(line))
                print('Line:', line)
                found = True
    return found

def authenticate(user):
    # if user doesn't exist
    if not (check_existence(user)):
        # then add user to storage
        # and welcome user
        add_new_user(user=user)
        return 11
    else:
        # welcome back user
        return 12
    