# THIS CODE IS MY OWN WORK, IT WAS WRITTEN WITHOUT CONSULTING
# A TUTOR OR CODE WRITTEN BY OTHER STUDENTS - Jason Ji

import sys

# parameter used
convergence = 0.0001
transition_prob = 0.85


# process the input and build a directed graph using adjacency list
def process_input(input_f):
    # rank stores the score for each individual node 
    rank = {}
    # graph stores the relationships between nodes
    # key is the node, value is a dictionary of sets, where graph[node]['in'] is a set 
    # of all the incoming nodes and graph[node]['out'] is a set of all outgoing nodes
    graph = {}

    file = open(input_f, 'r')
    while True:
        # Get next line from file
        line = file.readline()
        # if line is empty end of file is reached
        if not line:
            break
        line = line.strip()
        # skip the first and last line
        if line == "digraph {" or line == "}":
            continue

        start_node = line.split("->")[0].strip()
        end_node = line.split("->")[1].strip()

        # add start node and end node into rank
        if start_node not in rank:
            rank[start_node] = 0
        if end_node not in rank:
            rank[end_node] = 0

        # add start node and end node into graph
        if start_node not in graph:
            graph[start_node] = {}
            graph[start_node]['in'] = set()
            graph[start_node]['out'] = set()
        graph[start_node]['out'].add(end_node)
            
        if end_node not in graph:
            graph[end_node] = {}
            graph[end_node]['in'] = set()
            graph[end_node]['out'] = set()
        graph[end_node]['in'].add(start_node)
    file.close()

    return rank, graph

# write final page rank to the output csv file
def write_output(rank,output_f):
    # sort the rank from highest to lowest
    rank_sorted = {key : value for key, value in sorted(rank.items(), key= lambda item: item[1], reverse=True)}

    # write to output
    file = open(output_f, 'w')
    file.write("vertex,pagerank\n")
    for vertex, rank in rank_sorted.items():
        file.write(vertex + "," + str(rank) + "\n")
    file.close()

# pagerank algorithm
def page_rank(rank, graph):
    # first set ranks of all nodes to 1/n
    n = len(rank)
    for node in rank.keys():
        rank[node] = 1.0/n

    sum_diff = 1
    # while the rank for each node doesn't converge
    while sum_diff > convergence:
        rank_new = {}
        sum_rank = 0

        # compute the new rank for every node in the graph
        for node in rank.keys():
            node_rank = 0
            for in_node in graph[node]['in']:  
                d = len(graph[in_node]['out'])
                node_rank+= transition_prob * rank[in_node]/d
            rank_new[node] = node_rank
            sum_rank += node_rank
            
        # re-insert the leaked pagerank
        for node in rank.keys():
            rank_new[node]+= (1.0-sum_rank)/n

        # update the change in rank
        sum_diff = 0
        for node in rank.keys():
            sum_diff += abs(rank_new[node]-rank[node])
        
        # update the rank
        rank = rank_new
    
    return rank


def main(input_f, output_f):
    rank, graph = process_input(input_f)
    rank = page_rank(rank, graph)
    write_output(rank, output_f)


if __name__ == '__main__':
    # take input from user in the order: input file name and output file name
    input_f = ''
    output_f = ''
    for i, arg in enumerate(sys.argv):
        if i == 0:
            continue
        if i == 1:
            input_f = arg
        if i == 2:
            output_f = arg       

    main(input_f,output_f)