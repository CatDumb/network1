def find_index(my_list, my_element):
    index = my_list.index(my_element)
    return index


# my_list = ['Nho', 'Thaozz', 'Ichiramen', 'SinKawaii']
# print(find_index(my_list=my_list, my_element='SinKawaii'))

def get_address_from_string(raw_foreign_addr):
    raw_foreign_addr = raw_foreign_addr.strip("()")
    foreign_ip = raw_foreign_addr.split(', ')[0]
    foreign_ip = foreign_ip.replace("'", "")
    foreign_port = raw_foreign_addr.split(', ')[1]
    foreign_addr = (foreign_ip, int(foreign_port))
    return foreign_addr