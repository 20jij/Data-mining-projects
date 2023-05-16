import sys
from collections import defaultdict


# first delete all infrequent 1 set, then for generate all combination of k=2,k=3, k=4 from original transaction, 
# keep track of count, remove infrequent, then loop through data to find support for each. 


# itertools is used to generate all subsets of a an itemset
import itertools

# itemset object


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


# function that find all frequent (>= min support) 1-itemsets
def find_frequent_1_itemsets(database,min_supp):
    # L1 is a dictionary that stores the tuple of 1-itemset as key and support as value
    L1 = {}
    for transaction in database:
        for item in transaction:
            if (item,) in L1:
                L1[(item,)]+=1
            else:
                L1[(item,)]=1
    # remove infrequent 1-itemsets
    remove = set()
    for item, count in L1.items():
        if count < min_supp:
            remove.add(item)
    for item in remove:
        L1.pop(item)
    return L1

        


# function that joins and prunes the itemsets, returns a set of itemsets
def apriori_gen(L_k):
    C_k = set()
    for l1, support in L_k.items():
        for l2, support in L_k.items():
            # don't join with itself 
            if l1==l2:
                continue
            l1_key = l1[0:len(l1)-1]
            l2_key = l2[0:len(l2)-1]
            # join step
            if l1_key==l2_key:
                # join the two itemsets by adding the last item of l2 to l1
                c = l1+(l2[-1],)
                # sort the transaction to make sure the key is in order
                c = tuple(sorted(c))
                # prune step, if subsets are all frequent, add it to C_k
                if not has_infrequent_subset(c, L_k):
                    C_k.add(c)

    return C_k

def has_infrequent_subset(c, L_k ):
    # find all k-1 subsets of c
    subsets = tuple(itertools.combinations(c, len(c)-1))
    # print(subsets)
    for subset in subsets:
        subset = tuple(sorted(subset))
        if subset not in L_k:
            return True
    return False



def main(input_f, min_supp, output_f):

    database = process_input(input_f)

    L1 = find_frequent_1_itemsets(database, min_supp)

    # write the frequent 1 itemsets to the output file
    with open(output_f,"w+") as f:
        for itemset, support in L1.items():
            line = ""
            for item in itemset:
                line += str(item)
                line += " "
            line += "(" + str(support) + ")" + "\n"
            f.write(line)

    # remove the infrequent 1 itemsets from the database
    for transaction in database:
        for item in transaction:
            if (item,) not in L1.keys():
                transaction.remove(item)

    # generate all possible two 

    L_k = L1
    k = 2
    
    while len(L_k)!=0:
        C_k = apriori_gen(L_k)

        # find the supports for C_k, each support is first initialized to 0
        C_k_supp = defaultdict(lambda: 0)
        for transaction in database:
            # count the number of appearance of an itemset among all transactions
            for itemset in C_k:
                if set(itemset).issubset(transaction):
                    C_k_supp[itemset] +=1
        # filter out itemsets in C_k that don't satisfy min support
        L_k = {}
        for itemset, support in C_k_supp.items():
            if support>=min_supp:
                L_k[itemset] = support
                 # write the frequent k itemsets to the output file
                with open(output_f,"a") as f:
                    line = ""
                    for item in itemset:
                        line += str(item)
                        line += " "
                    line += "(" + str(support) + ")" + "\n"
                    f.write(line)
        # print("L_k", L_k)
        k+=1



    
    # print(L1)

    # print(input_f,min_supp,output_f)






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

    main(input_f,min_supp,output_f)
