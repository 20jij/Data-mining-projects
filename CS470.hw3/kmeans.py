# THIS CODE IS MY OWN WORK, IT WAS WRITTEN WITHOUT CONSULTING
# A TUTOR OR CODE WRITTEN BY OTHER STUDENTS - Jason Ji


import sys
import pandas as pd
import random
import math


# process the input file by asigning each data entry a key
# return a dictionary that store the data entry key and actual data as value
def process_input(input_f):
    database = {}
    df = pd.read_csv(input_f, sep=',',header=None)

    # data preprocessing for iris.data
    # drop the last column that is not numerical
    df = df.iloc[:, :-1]

    # data preprocessing for buddymove_holidayiq.csv 
    # drop the first row and column, which are categorical 
    # df = df.iloc[1: , :]
    # df = df.iloc[: , 1:]
    # df.reset_index(drop=True, inplace=True)

    
    for index, row in df.iterrows():
        # convert to numeric
        row = pd.to_numeric(row)
        database[index] = row.tolist()

    return database


# function that writes to the output file
def write_output(database, data_cluster_map, sse, silhoutte, output_f):
    with open(output_f,"w+") as f:
        for data_id in database.keys():
            line = str(data_cluster_map[data_id]) + "\n"
            f.write(line)
        f.write(str(sse)+"\n")
        f.write(str(silhoutte)+"\n")
    
# function that calculates the distance between two data using euclidean distance
def calculate_distance(v1, v2):
    summ = 0
    for i in range(len(v1)):
        x1 = v1[i]
        x2 = v2[i]
        summ += (x2-x1)**2
    return math.sqrt(summ)

# function that calculates the centroid of a list of data entry using the average
def calculate_centroid(data):
    summ = [0]* len(data[0])
    for entry in data:
        for i in range(len(entry)):
            summ[i] += entry[i]
    centroid = [summ[index]/len(data) for index in range(len(summ)) ]
    return centroid
        
# kmeans algorithm
def kmeans(database, k):
    # map each data id to the cluster it belongs
    data_cluster_map = {}
    for i in range(len(database)):
        data_cluster_map.update({i: 0})

    # randomly select k data entries as initial centroids 
    random_index = random.sample(range(0, 150),k)
    centroids = []
    for index in random_index:
        centroids.append(database[index])
    
    # map cluster id to its centroid location
    clusterID_centroid_map = {}
    for cluster_id, centroid in enumerate(centroids):
        clusterID_centroid_map[cluster_id] = centroid


    # assign each data entry in the original database to the closest cluster/centroid 
    for data_id, data in database.items():
        cluster_belong = 0
        min_dist = float('inf')
        for cluster_id, centroid in clusterID_centroid_map.items():
            dist = calculate_distance(centroid, data)
            if dist<min_dist:
                cluster_belong = cluster_id
                min_dist = dist
        data_cluster_map[data_id] = cluster_belong
    
    # continue to calculate the new centroid for each and update the distance until the 
    # centroids converge
    converged = False
    while not converged:

        converged = True

        # calculate new centroid location
        # cluster_data is used to find all points in each cluster beforehand
        # to prevent inner loops, therefore optimizing computation time
        cluster_data = {}
        for i in range(k):
            cluster_data.update({i: []})
        for data_id, cluster_id in data_cluster_map.items():
            cluster_data[cluster_id].append(database[data_id])

        for cluster_id, data_points in cluster_data.items():
            new_centroid = calculate_centroid(data_points)
            old_centroid = clusterID_centroid_map[int(cluster_id)]
            # check for convergence
            if set(new_centroid)!=set(old_centroid):
                converged = False
            # update the new centroid location
            clusterID_centroid_map[cluster_id] = new_centroid
    
        # reassign each data entry to the closest centroid to form cluster
        for data_id, data in database.items():
            cluster_belong = data_cluster_map[data_id]
            min_dist = float('inf')
            for cluster_id, centroid in clusterID_centroid_map.items():
                dist = calculate_distance(centroid, data)
                if dist<min_dist:
                    cluster_belong = cluster_id
                    min_dist = dist
            data_cluster_map[data_id] = cluster_belong


    # compute sum of squared errors and Silhoutte coefficient
    sse = 0
    silhoutte = 0

    # cluster data is used to store all data for each cluster for the 
    # following computation of silhoutte coefficient
    cluster_data = {}
    for i in range(k):
        cluster_data.update({i: []})
    for data_id, cluster_id in data_cluster_map.items():
        cluster_data[cluster_id].append(database[data_id])
    
    # loop through all data entry to compute sse and silhoutte
    for data_id, data in database.items():
        cluster_id = data_cluster_map[data_id]
        centroid = clusterID_centroid_map[cluster_id]
        sse += calculate_distance(data, centroid)**2
        # a is the average distance between data and all other objects in the cluster to which data belongs
        a = 0
        for other_data in cluster_data[cluster_id]:
            a += calculate_distance(data, other_data)
        a = a/(len(cluster_data[cluster_id])-1)
        # b is the minimum average distance from data to all clusters to which data does not belong
        b = float('inf')
        for cluster_id_other in cluster_data.keys():
            # skip the current cluster
            if cluster_id_other == cluster_id:
                continue
            avg_dist = 0
            for other_data in cluster_data[cluster_id_other]:
                avg_dist += calculate_distance(data, other_data)
            avg_dist = avg_dist/len(cluster_data[cluster_id_other])
            b = min(b, avg_dist)

        silhoutte += (b-a)/max(a,b)

    silhoutte = silhoutte/len(database)
    return data_cluster_map, sse, silhoutte
    


def main(input_f, k, output_f):
    database = process_input(input_f)
    data_cluster_map, sse, silhoutte = kmeans(database, k)
    write_output(database, data_cluster_map, sse, silhoutte, output_f)



if __name__ == '__main__':
    # take input from user in the order: input file name, k as the number of clusters, and output file name
    input_f = ''
    output_f = ''
    k = None
    for i, arg in enumerate(sys.argv):
        if i == 0:
            continue
        if i == 1:
            input_f = arg
        if i == 2:
            k = int(arg)
        if i == 3:
            output_f = arg

    main(input_f,k,output_f)