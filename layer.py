'''
Created on Dec, 2018

@author: Zixiao Yu
'''

import os
import json
import numpy
import csv


'''
Input files: movies800.json, reverseDict.json. 
Output files: output is 3 json files(layer1, layer2, layer3) in following format:
    not filter:
        All_final_layerindex
    with filters
    1. genre_final_layerindex
    2. agedown_to_ageup_layerindex

Obtain the Input files from @Jian.
Ask @Jian how to set up and the upload the output json files to S3 service. 

cluster_l1 and cluster_l2 is per-defined by @Fiona and @Di. if they change it, the cluster and tags name in these two
need modify.

'''

score_dict = {}

#--------------initial parameter--------------
pirority_weight = 1
release_weight = 1
promotion_weight = 1
starRating_weight = 1
cluster_l1 =[["animal"],
             ["superhero", "star war"],
             ["magic and fantasy characters"],
             ["robots","vehicles","toys","foods","sports",],
             ["ordinary people"],
             ["alien", "space"],["monster", "ghost", "vampire"],
             ["princess", "prince", "queen", "king",	"fairy", "elf", "mermaid", "smurf","snowman"]]
cluster_l2 = ["PG-13 & LA", "PG & LA", "PG-13 & Animation", "PG & Animation"]
tag2group = {}
#
#
layer_min_cluster = 1
# l1_max_tags=0
# l2_max_tags=0
# l3_max_tags=0
#
# l1_min_coverage = 0
l2_min_coverage = 0.99
# l3_min_coverage = 0
#
# l1_single_max_coverage = 0
l2_single_max_coverage = 1
# l3_single_max_coverage = 0


# setting_flag = 2
#
# if setting_flag == 1:
#     genre_name = 'ALL'
# elif setting_flag ==2:
#     genre_filter = ['music', 'musician', 'musical','Musical','Music','Musician']
#     genre_name = 'Music'
# elif setting_flag ==3:
#     genre_filter = ['family']
#     genre_name = 'Family'
# elif setting_flag ==4:
#     genre_filter = ['action/adventure']
#     genre_name = 'Adventure'
# elif setting_flag ==5:
#     genre_filter = ['comedy']
#     genre_name = 'Comedy'
# else:
#     print('Error')

#--------------initial end-------------------


class movie():

    '''
    movie class

    id: movie id
    releaseData: movie release year
    startRating: movie Rating
    mainCharacter: movie main Character
    secCharacter : movie second Character
    genre: movie genres
    ageRange: movie age range
    isAnimate: the movie is animation or not
    isAge13 : is this movie recommend watching age under 13
    layer2Cluster: movie Cluster name for layer2 in map (PG is under 13, PG-13 is above 13, Animation is animation, LA is Liveaction)
    promotion: movie have promotion score
    tag: all movie tags, include metadata from rovi + TCL manual data (manual tags need to extend by current manual tag
        parent tags and children tags)
    tags: the tag socre for each tag, main Character( and it's parents tags) score is 2,
     second Character score (and its' parents tags) is 1
    get_score: calculate movie score under current cluster
    get_score_split: a help function to split the score
    '''

    def __init__(self, data):
        self.id = data['id']
        self.releaseDate = int(data['releasedDate'])
        self.starRating = int(round(float(data['starRating'])))
        self.mainCharacter = data['mainCharacter']
        self.secCharacter = data['secondaryCharacter']
        self.genre = data['tag']
        self.ageRange = data['ageRange']
        self.isAnimate = data["isAnimated"]
        self.isAge13 = data["age13"]
        #self.isAge13 = True # only use for test------------------------------------------------------------------------------
        self.layer2Cluter = ("PG-13" if self.isAge13 else "PG" )+" & "+ ( "Animation" if self.isAnimate else "LA")
        if 'promotion' not in data:
            self.promotion = 0
        else:
            self.promotion = data['promotion']

        self.tag = data['tag']+self.mainCharacter+self.secCharacter
        for group_tag in self.mainCharacter:
            if group_tag in tag2group:
                self.tag += tag2group[group_tag]
        for group_tag in self.secCharacter:
            if group_tag in tag2group:
                self.tag += tag2group[group_tag]
        self.tag = list(set(self.tag))

        self.tags={}
        #manual tags need to be extended by current manual tag's parent tags and children tags, use reverse_dict to find them

        for tag in self.tag:
            group = []
            if tag in self.mainCharacter:
                self.tags[tag]=2
                if tag in tag2group:
                    for group_tag in tag2group[tag]:
                        self.tags[group_tag] = 2
            elif tag in self.secCharacter:
                self.tags[tag]= 1
                if tag in tag2group:
                    for group_tag in tag2group[tag]:
                        if group_tag in self.tags and self.tags[group_tag] == 2:
                            continue
                        else:
                            self.tags[group_tag] = 1
            elif tag in self.tags:
                continue
            else:
                self.tags[tag]=0
        self.filters = self.tag

    def get_score(self, clusters_name):
        '''
        get the movie score in current cluster,
        score = w1*tags_score + w2*release_score + w3*rating_score + w4*promotion_score
        :param clusters_name:
        :return: score
        '''
        score = 0
        for cluster_name in clusters_name:
            if cluster_name not in self.tags:
                return score

            score_new = pirority_weight * self.tags[cluster_name] + release_weight * release_score(self.releaseDate)\
                        + starRating_weight * self.starRating+promotion_weight*self.promotion
            if cluster_name == self.mainCharacter and len(self.mainCharacter)>1:
                score_new -=1
            score = max(score_new, score)
        return score
    def get_score_split(self, clusters_name):
        '''
        get movie score in current cluster and get score in separate format for score evaluation.
        :param clusters_name:
        :return: score
        '''
        character_score = 0
        releasedate_score = 0
        starRating_score = 0
        total_score = 0
        score_old = 0
        score = [character_score,releasedate_score,starRating_score,total_score]
        for cluster_name in clusters_name:
            if cluster_name not in self.tags:
                score_new = -1
            else:
                score_new = pirority_weight * self.tags[cluster_name] + release_weight * release_score(self.releaseDate)\
                            + starRating_weight * self.starRating+promotion_weight*self.promotion
            if cluster_name == self.mainCharacter and len(self.mainCharacter)>1:
                score_new -=1
            if score_new > score_old:

                character_score = pirority_weight*self.tags[cluster_name]
                releasedate_score = release_score(self.releaseDate)
                starRating_score =  starRating_weight * self.starRating
                total_score = character_score + releasedate_score+starRating_score
                score =  "%f:%f:%f:%f" % (character_score,releasedate_score,starRating_score,total_score)
            score_old = max(score_new, score_old)

        return score,total_score

def release_score(releaseDate):
    '''
    :param releaseDate:
    :return: release data relative score
    '''
    score = 0
    if releaseDate > 2016:
        score =5
    elif 2016>= releaseDate >2014:
        score =3
    elif 2014 >= releaseDate >2010:
        score = 2
    elif 2010 >= releaseDate > 2000:
        score = 1
    else:
        score = 0
    return score

def file_read(filename, reverse_tag_dict):
    '''
    load movies json data and reverse dict
    the reverse_tag_dict is use to find the parents/children tags for current manual tag
    :param filename: movies json data location
    :param reverse_tag_dict:
    :return: data and reverse_dict
    '''
    with open (filename) as f:
        data = json.load(f)
    with open (reverse_tag_dict) as f:
        reverse_dict = json.load(f)
    return data, reverse_dict

def data_initialize(data, reverse_dict_raw):
    '''
    initial the movies by using movie class
    :param data: movies json data
    :param reverse_dict_raw:
    :return: movies
    '''
    for key in reverse_dict_raw:
        tag2group[key] = reverse_dict_raw[key]
    movies = []
    for key in data:
        movies.append(movie(data[key]))

    return movies


def movies_filter(movies, filter_tags, filter_age_up= None, filter_age_down = None ):
    '''
    get movie after filtered
    :param movies: all movies
    :param filter_tags: the movie with these tags will be keep
    :param filter_age_up:
    :param filter_age_down:
    :return: movies after filtered
    '''

    result = []

    if filter_tags ==None and filter_age_up != None:
        for movie in movies:
            if filter_age_down<=movie.ageRange <=filter_age_up:
                result.append(movie)
            else:
                continue
    elif filter_age_up != None and filter_tags != None:
        for movie in movies:

            for tag in filter_tags:
                if tag in movie.filters and filter_age_down<=movie.ageRange <=filter_age_up:
                    result.append(movie)
            else:
                continue
    else:
        for movie in movies:
            for tag in filter_tags:
                if tag in movie.filters:
                    result.append(movie)
            else:
                continue
    return result

#--------------data convert end----------------------------
def layer_1_ranking(movies):
    '''

    :param movies:
    :return: the layer 1 movies ranking under cluster name
    '''
    results = {}
    for cluster_name in cluster_l1:
        str ='-'
        results[str.join(cluster_name)] = sort_layer(get_layer_1_ranking(movies, cluster_name), cluster_name)
    return results

def get_layer_1_ranking(movies, clusters_name):
    '''
    a help function for ranking
    :param movies:
    :param clusters_name:
    :return:
    '''
    results = []
    for cluster_name in clusters_name:
        for movie in movies :
            if cluster_name in movie.tags and movie not in results:
                results.append(movie)
    return results

def sort_layer(movies, cluster_name):
    '''
    sort movies in current cluster by using movies score
    :param movies:
    :param cluster_name: sort movie by current cluster name
    :return: sorted movies
    '''

    cur_cluster_score_list = {}
    cur_dict = {}
    for movie in movies:
        score_split, total_score = movie.get_score_split(cluster_name)

        cur_cluster_score_list[movie.id] = [total_score, score_split]
    cur_cluster_score_list = sorted(cur_cluster_score_list.items(), key=lambda kv: kv[1][0], reverse= True)
    for cur in cur_cluster_score_list:
        cur_dict[cur[0]] = cur[1]
    if not score_dict.__contains__('-'.join(cluster_name)):
        score_dict['-'.join(cluster_name)] = cur_dict
    else:
        prv_cur_dict = score_dict[''.join(cluster_name)]
        cur_dict = Merge(prv_cur_dict,cur_dict)
        score_dict['-'.join(cluster_name)] = cur_dict




    return sorted(movies, key = lambda movie:movie.get_score(cluster_name),reverse=True)
def Merge(dict1, dict2):
    # merge two dict
    res = {**dict1, **dict2}
    return res
def my_rank(dict):
    for key in dict:
        value = dict[key][0]
    return value
def layer_next_cluster(movies, parentTag):
    '''
    Calculate the next layer cluster name and put the movie into these cluster
    Currently only use in layer 3
    function example:
        1. 100 movies have a same parentTag P.
        2. get all the tags used by this 100 movies, tag_pool = [t1, t2, t3 ....]
        3. 50 movies have t1, 48 movies have t2, 45 movies have t3 ...., no tn shared by more than 50 movies( t1 has
            the most share rate)
        4. use 3 tags in  tag_pool can get coverage rate more than l2_single_max_coverage then use this 3 tags for next
            layer clusters. coverage rate = (movies have these tags/ all movies)

    :param movies: current processing movies
    :param parentTag: the upper layer tag of current processing movies
    :return:
    '''
    tags_pool = {}
    for movie in movies:
        for tag in movie.tags:
            if parentTag.__contains__(tag):
                continue
            elif tag not in tags_pool:
                tags_pool[tag] = 1
            else:
                tags_pool[tag] = tags_pool[tag]+1

    for tag in list(tags_pool):
        if layer_tag_converage(tags_pool[tag],len(movies)) > l2_single_max_coverage:
            tags_pool.pop(tag,None)
    result = get_next_cluster(tags_pool,movies)
    return result

def layer_l2_cluster(movies):
    '''
    put the movie into 4 different layer 2 clusters

    :param movies:
    :return: 4 different layer 2 clusters results
    '''
    results = {}
    result_PG_Ani =[]
    result_PG_LA = []
    result_PG13_Ani =[]
    result13_PG_LA = []
    #"PG-13 & LA", "PG & LA", "PG-13 & Animation", "PG & Animation"
    for movie in movies:
        if movie.layer2Cluter == cluster_l2[0]:
            result13_PG_LA.append(movie)
        elif movie.layer2Cluter == cluster_l2[1]:
            result_PG_LA.append(movie)
        elif movie.layer2Cluter == cluster_l2[2]:
            result_PG13_Ani.append(movie)
        elif movie.layer2Cluter == cluster_l2[3]:
            result_PG_Ani.append(movie)
        else:
            continue

    results[cluster_l2[0]] = result13_PG_LA
    results[cluster_l2[1]] = result_PG_LA
    results[cluster_l2[2]] = result_PG13_Ani
    results[cluster_l2[3]] = result_PG_Ani


    return results



def layer_tag_converage(cur_movies_number,len_movie):
    coverage = cur_movies_number/(len_movie)
    return coverage

def get_next_cluster(tags,movies):
    '''
    similar to layer_next_cluster
    :param tags:
    :param movies:
    :return:
    '''
    cur_movie = {}
    cluster_movies_numbers = len(movies)
    next_all_cluster = {}
    next_cluster = []

    sort_tags=sorted(tags.items(), key = lambda kv:kv[1], reverse=True)

    for tag in sort_tags:
        cur_cluster_movies = []
        for movie in movies:
            if tag[0] in movie.tags:
                if movie not in cur_movie:
                    cur_movie[movie] = 1
                cur_cluster_movies.append(movie)
        next_all_cluster[tag[0]] = sort_layer(cur_cluster_movies,[tag[0]])

        cur_moveies_numbers = len(cur_movie)
        next_cluster.append(tag)
        if (cur_moveies_numbers/ cluster_movies_numbers) > l2_min_coverage and  len(next_all_cluster) > layer_min_cluster:
            break

    return next_all_cluster







# initial movies data and reverse dict
movies_raw, reverse_dict_raw=file_read("movie800.json", "reverseDict.json")
movies=data_initialize(movies_raw, reverse_dict_raw)





#use movie filter
setting_flag = 1
age_down =  3
age_up = 5

if setting_flag == 1:
    genre_name = 'ALL'
elif setting_flag ==2:
    genre_filter = ['music', 'musician', 'musical','Musical','Music','Musician']
    genre_name = 'Music'
elif setting_flag ==3:
    genre_filter = ['family']
    genre_name = 'Family'
elif setting_flag ==4:
    genre_filter = ['action/adventure']
    genre_name = 'Adventure'
elif setting_flag ==5:
    genre_filter = ['comedy']
    genre_name = 'Comedy'
else:
    print('Error')
if setting_flag != 1:
    movies = movies_filter(movies, genre_filter,filter_age_up=age_up,filter_age_down=age_down)
if age_up != None and setting_flag == 1:
    movies = movies_filter(movies, None, filter_age_up=age_up,filter_age_down=age_down)
    genre_name = str(age_down) + 'to' +str(age_up)



#get layer 1
l1=layer_1_ranking(movies)
results_l2 = {}
results_l3 = {}

# get layer 2
for cluster in l1:
    results_l2[cluster] = layer_l2_cluster(l1[cluster])

# get layer 3
for l1_tag in results_l2:
    parent = l1_tag.split("-")
    result_l3_part = {}
    for age_tage in results_l2[l1_tag]:
        result_l3_part[l1_tag +"+"+ age_tage] = layer_next_cluster(results_l2[l1_tag][age_tage], parent)
    results_l3[l1_tag] = result_l3_part
print("end")
# results_l2 = {}
# result_l3 = {}
#
# for key in l1:
#     parent = []
#     parent.append(key)
#     results_l2[key] = layer_next_cluster(l1[key], parent)
#     #results_l2.append(layer_next_cluster(l1[key], parent))
#
# for tag_l1 in results_l2:
#     parent = []
#     parent.append(tag_l1)
#     result_l3_part = {}
#     for tag_l2 in results_l2[tag_l1]:
#         parent.append(tag_l2)
#         result_l3_part[tag_l1+"-"+tag_l2] = layer_next_cluster(results_l2[tag_l1][tag_l2], parent)
#     result_l3[tag_l1] = result_l3_part

# print(1)
#
final_l1 = {}
final_l2 = {}
final_l3 = {}

# use pool to prevent movies repetition in layer 1 and layer 2
final_l1_pool = []
final_l2_pool = []

final_l1_count = {}
final_l2_count = {}
final_l3_count = {}


final_l1_pool_correct = {}


#get final layer 1
for cluster in l1:
    l1_part = []
    l1_part_8 = []
    count = 0
    for movie in l1[cluster]:
        if movie.id in final_l1_pool:
            continue
        if count < 8:
            final_l1_pool.append(movie.id)
            l1_part_8.append(movie.id)
        count+=1
        l1_part.append(movie.id)
    final_l1_pool_correct[cluster] = l1_part_8
    final_l1[cluster]=l1_part
    final_l1_count[cluster] = count


#get final layer 2
for cluster_1 in results_l2:
    skip_list = []
    for cluster in final_l1_pool_correct:
        if cluster == cluster_1:
            continue
        for movie in final_l1_pool_correct[cluster]:
            skip_list.append(movie)

    for cluster_2 in results_l2[cluster_1]:
        l2_part = []
        count = 0
        for movie in results_l2[cluster_1][cluster_2]:
            if movie.id in final_l2_pool:
                    continue
            if movie.id in skip_list:
                continue
            if count < 8:
                final_l2_pool.append(movie.id)
            count+=1
            l2_part.append(movie.id)
        final_l2_count[cluster_1+"+"+cluster_2] = count
        final_l2[cluster_1+"+"+cluster_2] = l2_part


# get final layer 3
for cluster_1 in results_l3:
    final_l3_pool = []
    for cluster_2 in results_l3[cluster_1]:
        for cluster_3 in results_l3[cluster_1][cluster_2]:
            count = 0
            l3_part = []
            for movie in results_l3[cluster_1][cluster_2][cluster_3]:
                if movie.id in final_l3_pool:
                    continue
                if count < 800:
                    final_l3_pool.append(movie.id)
                count+=1
                l3_part.append(movie.id)
            final_l3_count[cluster_2+"+"+cluster_3] = count
            final_l3[cluster_2+"+"+cluster_3] = l3_part
        if results_l3[cluster_1][cluster_2].__len__() == 0:
            final_l3_count[cluster_2+"+"+"none"] = count
            final_l3[cluster_2+"+"+"none"] = ""



#store the score file in json file
with open('score_dict.json','w')as f:
    json.dump(score_dict,f,indent=1, sort_keys=True)

# store the result in json file
result_l1 = json.dumps(list(final_l1.items()))
result_l2 = json.dumps(list(final_l2.items()))
result_l3 = json.dumps(list(final_l3.items()))
with open(genre_name+'_final_l1.json','w+') as outfile:
    json.dump(final_l1,outfile,indent=4)
#print(result_l1)

with open(genre_name+'_final_l2.json','w+') as outfile:
    json.dump(final_l2,outfile,indent=4)

with open(genre_name+'_final_l3.json','w+') as outfile:
    json.dump(final_l3,outfile,indent=4)

# with open(genre_name+'_final_l1_count.json','w+') as outfile:
#     json.dump(final_l1_count,outfile,indent=4)
# #print(result_l1)
#
# with open(genre_name+'_final_l2_count.json','w+') as outfile:
#     json.dump(final_l2_count,outfile,indent=4)
#
# with open(genre_name+'_final_l3_count.json','w+') as outfile:
#     json.dump(final_l3_count,outfile,indent=4)
#print(result_l1)

