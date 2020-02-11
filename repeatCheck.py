import json


with open('Adventure_final_l1.json', 'r') as f:
    json_data = json.loads(f.read())


fix_dict = {}
for item in json_data:
    keys = item.split('+')
    key = keys [0]
    for movie_id in json_data[item]:
        if key not in fix_dict:
            key_list = {}
            fix_dict[key] = key_list
        if movie_id not in fix_dict[key]:
            fix_dict[key][movie_id] = 1
        else:
            fix_dict[key][movie_id]+=1
            print("repeats: "+str(key)+' -- '+ str(movie_id)+ " ,times"+str(fix_dict[key][movie_id]) )



print('end')