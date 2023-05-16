# THIS CODE IS MY OWN WORK, IT WAS WRITTEN WITHOUT CONSULTING
# A TUTOR OR CODE WRITTEN BY OTHER STUDENTS - Jason Ji


import sys
import itertools
import time


# the algorithm logic: 
# instead of keeping track of itemsets that are frequent, we remove itemsets that 
# are non frequent from the database. 
# first find all frequent 1 itemsets, delete all infrequent 1 set from databse (transactions)
# then as we increase k, for each k we generate all potential candidates frequent itemsets from transactions,
# prune infrequent itemsets, and remove items in original transactions that are doesn't appear 
# in frequent itemsets because we don't need to consider them for the next k if they are already infrequent. 
# terminate when there is no more frequent itemsets that can be generated. 


# process the input and store original transactions in a dictionary
def process_input(input_f):
    # database is a list of lists, each representing a transaction
    database =  []
    with open(input_f) as f:
        count = 1
        lines = f.readlines()
        for line in lines:
            transaction = line.strip().split(' ')
            # convert into a list of integers
            for i in range(0, len(transaction)):
                transaction[i] = int(transaction[i])
            database.append(transaction)
    return database


# find all frequent (>= min support) 1-itemsets
def find_frequent_1_itemsets(database,min_supp):
    # C1 is a dictionary that stores the tuple of 1-itemset as key and support as value
    C1 = {}
    for transaction in database:
        for item in transaction:
            if (item,) in C1:
                C1[(item,)]+=1
            else:
                C1[(item,)]=1
    # remove infrequent 1-itemsets
    remove = set()
    for item, count in C1.items():
        if count < min_supp:
            remove.add(item)
    for item in remove:
        C1.pop(item)
    return C1

        
# write the all frequent itemsets to the output file
def write_output(frequent_itemsets, output_f):
    with open(output_f,"w+") as f:
        for itemset, support in frequent_itemsets.items():
            line = ""
            for item in itemset:
                line += str(item)
                line += " "
            line += "(" + str(support) + ")" + "\n"
            f.write(line)
            

# find all k subsets of each transaction as potential frequent itemsets
# then prunes the infrequent itemsets, returns a dictionary of frequent k-itemsets with their supports
def apriori_gen(database, min_supp, k):
    Ck = {}
    for transaction in database:
        for itemset in itertools.combinations(transaction, k):
            # sort the itemset and convert it to tuple (for dictionary key)
            itemset = tuple(sorted(itemset))
            if itemset in Ck:
                Ck[itemset]+=1
            else:
                Ck[itemset] = 1
    # prune the infrequent itemsets
    Ck = {itemset: support for itemset, support in Ck.items() if support >= min_supp}
    return Ck



def main(input_f, min_supp, output_f):

    # stores the final output
    frequent_itemsets = {}

    database = process_input(input_f)

    C1 = find_frequent_1_itemsets(database, min_supp)
    # add frequent-1-itemset to the output
    frequent_itemsets.update(C1)

    # remove the infrequent 1 itemsets from the database
    for transaction in database:
        for item in transaction:
            if (item,) not in C1.keys():
                transaction.remove(item)

    Ck = C1
    k = 2
    # iterate through all k to find all frequent-k-itemsets
    while len(Ck)!=0:
        Ck = apriori_gen(database, min_supp,k)
        # add frequent-k-itemsets to output
        frequent_itemsets.update(Ck)
        # remove item in each transactions that never appear in current frequent-k-itemsets 
        # because we don't need to consider them for the next k if they are already infrequent. 
        frequent_items = []
        for keys in Ck.keys():
            for item in keys:
                frequent_items.append(item)
        for transaction in database:
                for number in transaction:
                    if number not in frequent_items:
                        transaction.remove(number)
        k+=1

    # write the final output to output file
    write_output(frequent_itemsets, output_f)




if __name__ == '__main__':
    # take input from user in the order: input file name, threshold of min support count, and output file name
    input_f = ''
    output_f = ''
    min_supp = None
    for i, arg in enumerate(sys.argv):
        if i == 0:
            continue
        if i == 1:
            input_f = arg
        if i == 2:
            min_supp = int(arg)
        if i == 3:
            output_f = arg

    start_time = time.time()
    main(input_f,min_supp,output_f)
    duration = time.time() - start_time
    print("Runtime: ", duration)
