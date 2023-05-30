import csv
import re

# TASK 1

filenames = ['./Lesson2_data/info_1.txt'
             ,'./Lesson2_data/info_2.txt'
             ,'./Lesson2_data/info_3.txt']

def get_data(filenames):
    main_data = [["Изготовитель системы", "Название ОС", "Код продукта", "Тип системы"]]
    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []
    regexp_os_name = re.compile("Название ОС:(.*)$")
    regexp_os_prod = re.compile("Изготовитель ОС:(.*)$")
    regexp_os_code = re.compile("Код продукта:(.*)$")
    regexp_os_type = re.compile("Тип системы:(.*)$")

    for filename in filenames:
        with open(filename,"r", encoding='Windows-1251') as f_n:
            f_n_reader = csv.reader(f_n)
            for row in f_n_reader:
                search_result = regexp_os_name.search(row[0])
                if search_result:
                    os_name_list.append(search_result.group(1).strip())
                else:
                    search_result = regexp_os_prod.search(row[0])
                    if search_result:
                        os_prod_list.append(search_result.group(1).strip())
                    else:
                        search_result = regexp_os_code.search(row[0])
                        if search_result:
                            os_code_list.append(search_result.group(1).strip())
                        else:
                            search_result = regexp_os_type.search(row[0])
                            if search_result:
                                os_type_list.append(search_result.group(1).strip())

    for i in range(len(filenames)):
        main_data.append([os_prod_list[i], os_name_list[i], os_code_list[i], os_type_list[i]])
    return main_data


def write_to_csv(out_filename, in_filenames):
    out_data = get_data(in_filenames)
    with open(out_filename,"w", encoding='UTF-8') as f_n:
        f_n_writer = csv.writer(f_n)
        for row in out_data:
            f_n_writer.writerow(row)


write_to_csv('./Lesson2_data/lesson2_out.csv',filenames)


# TASK 2
import json


def write_order_to_json(item, quantity, price, buyer, date):
    dict_to_json ={
        "item" : item
        ,"quantity" : quantity
        ,"price" : price
        ,"buyer" : buyer
        ,"date" : date
    }
    with open('./Lesson2_data/orders.json', 'w') as f_n:
        json.dump(dict_to_json, f_n,  indent=4)

write_order_to_json("socks", 10, 15.5, "Me", "2023-05-30")


# TASK 3
import yaml


def write_data_to_yaml(dict_data):
    with open('./Lesson2_data/file.yaml', 'w') as f_n:
        yaml.dump(dict_data, f_n, default_flow_style = False, allow_unicode = True)

dict_data = {
    "List" : ["item 1", "item 2", "item 3"]
    ,"Integer" : 3
    ,"Dict" : {
        "Key1" : "20€"
        ,"Key2" : "10🚂"
        ,"Key3" : "15🎠"
    }
}

write_data_to_yaml(dict_data)
with open('./Lesson2_data/file.yaml', 'r') as f_n:
    dict_data_read = yaml.load(f_n)
    print(dict_data_read)
    print(dict_data)