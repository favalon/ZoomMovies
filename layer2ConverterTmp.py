import json
'''
Created on Dec, 2018

@author: Zixiao Yu
'''


'''
this is a tmp modification. Modify the layer 2 for the demo. 
layer 2 will only have 2 clusters, Animation and LiveAction in demo

'''
def read_file(layer2):
    with open(layer2, 'r') as f:
        dict_data = json.loads(f.read())

    return dict_data



def split_dict(layer2_dict):
    new_dict = {}
    for keys in layer2_dict:
        key = keys.split('+')
        key_l1 = key[0]
        key_l2 = key[1]
        if key_l2 == 'PG & LA':
            new_dict[keys] = layer2_dict[key_l1+'+PG-13 & LA'][4:8]
        elif key_l2 == 'PG & Animation':
            new_dict[keys] = layer2_dict[key_l1+'+PG-13 & Animation'][4:8]
        else:
            new_dict[keys] = layer2_dict[keys]
    return  new_dict

def split_dict_l3(layer2_dict):
    new_dict = {}
    for keys in layer2_dict:
        key = keys.split('+')
        key_l1 = key[0]
        key_l2 = key[1]
        key_l3 = key[2]
        if key_l2 == 'PG-13 & LA':
            length = int(len(layer2_dict[key_l1+'+PG-13 & LA+'+key_l3])/2)
            new_dict[keys] = layer2_dict[keys][0:length]
            new_dict[key_l1+'+PG & LA+'+key_l3] = layer2_dict[keys][length:-1]
        elif key_l2 == 'PG-13 & Animation':
            length = int(len(layer2_dict[key_l1+'+PG-13 & Animation+'+key_l3])/2)
            new_dict[keys] = layer2_dict[keys][0:length]
            new_dict[key_l1+'+PG & Animation+'+key_l3] = layer2_dict[keys][length:-1]
        else:
            length = int(len(layer2_dict[keys])/2)
            new_dict[keys] = layer2_dict[keys][0:length]
    return  new_dict


def final_converter(dict):
    sorted_key = sorted(dict.keys())
    # convert cluster name to general class name
    general_class = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    pre_key = ""
    class_count = -1
    for key in sorted_key:
        cur_key = key.split("+")[0]
        cur_extend = "+".join(key.split('+')[1:])
        if cur_key == pre_key:
            dict[general_class[class_count]+"+"+cur_extend] = dict.pop(key)
        elif class_count < len(general_class)-1:
            class_count+=1
            dict[general_class[class_count]+"+"+cur_extend] = dict.pop(key)
            pre_key = cur_key
    return dict

if __name__ == '__main__':
    setting_flag = 1
    age_down = 3
    age_up =None

    if setting_flag == 1:
        genre = 'ALL'
    elif setting_flag ==2:
        genre_filter = ['music', 'musician', 'musical','Musical','Music','Musician']
        genre= 'Music'
    elif setting_flag ==3:
        genre_filter = ['family']
        genre = 'Family'
    elif setting_flag ==4:
        genre_filter = ['action/adventure']
        genre = 'Adventure'
    elif setting_flag ==5:
        genre_filter = ['comedy']
        genre = 'Comedy'
    else:
        print('Error')

    if age_up != None and setting_flag == 1:
        genre= str(age_down) + 'to' +str(age_up)
    l2_dict = read_file(genre+'_final_l2.json')
    l3_dict = read_file(genre+'_final_l3.json')
    l2 = split_dict(l2_dict)
    with open(genre+'_final_l2.json','w')as f:
        json.dump(l2,f)
    l3 = split_dict_l3(l3_dict)
    with open(genre+'_final_l3.json','w')as f:
        json.dump(l3,f)

    l2 = final_converter(l2)
    l3 = final_converter(l3)
    print('end')
