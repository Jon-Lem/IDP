import numpy as np
import re
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform
from sklearn.metrics import silhouette_score
from sklearn.cluster import AgglomerativeClustering
from matplotlib import pyplot as plt

distcheck = 0

def simMatrix(output,goal):
    for k in range(len(goal)):
        models = []
        pattern = re.escape(goal[k]) + r' := {(.*)}'
        for line in output.split("\n"):
            match = re.match(pattern,line)
            if match:
                try: # If predicate
                    model = eval("[" + match.group(1) + "]")
                except: # If function
                    model = re.findall( r'->\s*(\w+)', match.group(1))
                    # print(model)
                    # print(len(model))
                    # exit()
                models.append(model)
        # print(models)
        if k==0:
            simMat = [[0 for _ in range(len(models))] for _ in range(len(models))]
        for i in range(len(models)):
            for j in range(len(models)):
                # distance = len(set(models[j]) - set(models[i]))
                distance = sum(x != y for x, y in zip(models[i], models[j]))
                if k==0:
                    simMat[i][j] = distance
                else:
                    simMat[i][j] += distance
                # print(f"simMat[{i}][{j}] = {simMat[i][j]}")
    
    return simMat
def plot_dendrogram(model, **kwargs):
    # Create linkage matrix and then plot the dendrogram

    # create the counts of samples under each node
    counts = np.zeros(model.children_.shape[0])
    n_samples = len(model.labels_)
    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1  # leaf node
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    linkage_matrix = np.column_stack(
        [model.children_, model.distances_, counts]
    ).astype(float)

    # Plot the corresponding dendrogram
    dendrogram(linkage_matrix, **kwargs)

def distCheck(simMat,solutions,k):
    # print(solutions)
    sum_distance = 0
    for i in range(len(solutions)):
        for j in range(len(solutions)):
            a = solutions[i]
            b = solutions[j]
            sum_distance += simMat[a][b]
            # print(f'(s{a+1},s{b+1}) -> {simMat[a][b]}')
    if(sum_distance//2 >= k):
        # print("distCheck 1")
        # print(solutions)
        # print(sum_distance/2)
        global distcheck
        distcheck=1
        return True
    else: 
        # print("distCheck 0")
        return False
    
def prettyPrint(simMat,solutions,k):
    dist = []
    for i in range(len(solutions)):
        for j in range(len(solutions)):
            a = solutions[i]
            b = solutions[j]
            dist.append(f'(s{a+1},s{b+1}) -> {simMat[a][b]}')
    distance = ','.join(dist)
    print('distance := {' + distance + '}.')
    print(f'k := {k}.')

def clusterComp(clusters:list,i:int,j:int,l:list):
    if clusters[i] != clusters[j] and l == []:
        return True
    elif clusters[i] != clusters[j] and l != [] :
        for item in l:
            if(clusters[j] == clusters[item]):
                return False
        return True
    else:
        return False

def clustering(simMat,k,n):
    # print(f'distance_threshold = {k//n}')
    linkage_type ='complete'
    best_sil = -1
    best_model = None
    for n_clusters in range(2,len(simMat)):
        clusterer = AgglomerativeClustering(metric='precomputed',n_clusters=n_clusters, linkage=linkage_type)
        model = clusterer.fit(simMat)
        cluster_labels = model.labels_
        silhouette_avg = silhouette_score(simMat, cluster_labels , metric="precomputed", )
        # if (silhouette_avg < 0.17):
        #     break
        # print("For n_clusters =" ,n_clusters, "The average silhouette_score is :", silhouette_avg,)
        if silhouette_avg > best_sil and n_clusters != 2:
            best_sil = silhouette_avg
            best_model = model
            num_cluster = n_clusters
    model = best_model

    # model = AgglomerativeClustering(
    # metric='precomputed',
    # n_clusters=None,
    # distance_threshold = k//n, #Wilt dat elke cluster een afstand van 7 met elkaar heeft
    # linkage=linkage_type
    # ).fit(simMat)

    print(f" Number of clusters: {model.n_clusters_}")
    if(model.n_clusters_ == 1):
        print('Solution is not satisfiable')
        exit()
    # print(set(list(model.labels_)))
    # solutions = [list(model.labels_).index(x) for x in set(list(model.labels_)) ]
    # solutions = solutions[:n]

    # plt.title("Hierarchical Clustering Dendrogram")
    # x = squareform(simMat)
    # temp = linkage(x, linkage_type)
    # dendrogram(temp, above_threshold_color="green", color_threshold=k//n , orientation='right')
    # plt.show()

    # plt.title("Hierarchical Clustering Dendrogram")
    # # plot the top three levels of the dendrogram
    # plot_dendrogram(model, truncate_mode="level", p=3)
    # plt.xlabel("Number of points in node (or index of point if no parenthesis).")
    # plt.show()

    solutions = []
    clusters = list(model.labels_)
    for i in range(len(clusters)):
        l = []
        for j in range(len(clusters)):
            if clusterComp(clusters,i,j,l): 
                if(simMat[i][j] >= k/n):
                    # print(f'(s{i},s{j}) -> {simMat[i][j]}')
                    if i not in solutions: solutions.append(i)
                    if j not in solutions: solutions.append(j)
                    l.append(j)
    # print(solutions)
    n_solutions=solutions[0:n]
    i = 0
    while not distCheck(simMat,n_solutions,k) and len(solutions) > n+i:
        i+=1
        n_solutions = solutions[i:n+i]
    # print(solutions)
    # print(n_solutions)
    solutions = n_solutions
    if(distcheck==0):
        print('Solution is not satisfiable')
        exit()
    prettyPrint(simMat,solutions,k)

    return