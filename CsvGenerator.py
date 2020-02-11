import csv
import json

def read_file(layer1, layer2, layer3, score_dict_file, movies_file):
    with open(score_dict_file, 'r') as f:
        dict_data = json.loads(f.read())
    with open(layer1, 'r') as f:
        layer1_data = json.loads(f.read())
    with open(layer2, 'r') as f:
        layer2_data = json.loads(f.read())
    with open(layer3, 'r') as f:
        layer3_data = json.loads(f.read())
    with open(movies_file, 'r') as f:
        movies = json.loads(f.read())
    return dict_data, layer1_data, layer2_data, layer3_data,movies
def one_row(csv_writer,layer,ranking,movie_id,moive_name,cluster_name,character_score,release_score,rating_score,total_score):
    csv_writer.writerow({'layer': layer, 'ranking': ranking, 'movie_id': movie_id, 'movie_name':moive_name, 'cluster_name':cluster_name, 'character_score': character_score,
                         'release_score': release_score, 'rating_score': rating_score, 'total_score':total_score})
def process_csv_file(csv_file,score_dict,layer_data,layer_index,movies_dict):
    layer_max_number = 0
    with open(csv_file, mode='w') as f:
        fieldnames = ['layer', 'ranking', 'movie_id', 'movie_name', "cluster_name",'character_score', 'release_score', 'rating_score', 'total_score']
        wr = csv.DictWriter(f,  fieldnames=fieldnames)
        wr.writeheader()
        if layer_index == 1:
            layer_max_number = 8
            for cluster_names in layer_data:
                count = 0
                for movie_id in layer_data[cluster_names]:
                    movie_name = movies_dict[movie_id]
                    total_score = score_dict[cluster_names][movie_id][0]
                    ranking = count
                    score_split = score_dict[cluster_names][movie_id][1].split(':')
                    char_score = score_split[0]
                    date_score = score_split[1]
                    rating_score = score_split[2]
                    one_row(wr,layer_index,ranking,movie_id,movie_name,cluster_names,char_score,date_score,rating_score,total_score)
                    count+=1
                    if count > layer_max_number:
                        break
        if layer_index == 2:
            layer_max_number = 8
            for cluster_names in layer_data:
                count = 0
                for movie_id in layer_data[cluster_names]:
                    movie_name = movies_dict[movie_id]
                    cluster_names = cluster_names.split('+')[0]
                    total_score = score_dict[cluster_names][movie_id][0]
                    ranking = count
                    score_split = score_dict[cluster_names][movie_id][1].split(':')
                    char_score = score_split[0]
                    date_score = score_split[1]
                    rating_score = score_split[2]
                    one_row(wr,layer_index,ranking,movie_id,movie_name,cluster_names,char_score,date_score,rating_score,total_score)
                    count+=1
                    if count > layer_max_number:
                        break
                    else:
                        continue
        if layer_index == 3:
            layer_max_number = 10000
            for cluster_names in layer_data:
                count = 0
                for movie_id in layer_data[cluster_names]:
                    movie_name = movies_dict[movie_id]
                    cluster_name = cluster_names.split('+')[2]
                    total_score = score_dict[cluster_name][movie_id][0]
                    ranking = count
                    score_split = score_dict[cluster_name][movie_id][1].split(':')
                    char_score = score_split[0]
                    date_score = score_split[1]
                    rating_score = score_split[2]
                    one_row(wr,layer_index,ranking,movie_id,movie_name,cluster_name,char_score,date_score,rating_score,total_score)
                    count+=1
                    if count > layer_max_number:
                        break


def get_movies_dict(movies):
    movies_dict = {}
    for movie in movies:
        movies_dict[movie] = movies[movie]['title']

    return movies_dict
if __name__ == '__main__':
    genre = 'ALL'
    score_dict, layer1_data,layer2_data,layer3_data, movies =  read_file(genre+'_final_l1.json',genre+'_final_l2.json',genre+'_final_l3.json','score_dict.json','movie800.json')
    movies_dict = get_movies_dict(movies)
    process_csv_file('csv_output/output_layer1_8csv.csv',score_dict,layer1_data,1,movies_dict)
    process_csv_file('csv_output/output_layer2_8csv.csv',score_dict,layer2_data,2,movies_dict)
    process_csv_file('csv_output/output_layer3_csv.csv',score_dict,layer3_data,3,movies_dict)
