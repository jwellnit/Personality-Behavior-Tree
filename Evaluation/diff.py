import sys

# polynomial hashing
def hash(line):
    total = 0
    # use 47 as a polynomial base
    for i in range(len(line)):
        total += ord(line[i])*47**i
    return total%1024

def diff():
    # open the file
    file = open(sys.argv[1]).read()
    lines = file.split("\n") #split by lines
    f1hash = []
    for l in lines:
       f1hash.append(hash(l)) #hash each line, saving in list?
    file = open(sys.argv[2]).read()
    lines = file.split("\n") #split by lines
    f2hash = []
    for l in lines:
       f2hash.append(hash(l)) #hash each line, saving in list?
    lcs(f1hash, f2hash)

def lcs(list1, list2):
    #This function expects to get two lists of hash values to compare
    #We set len1 and len2 to use when constructing the matrix
    len1 = len(list1)+1
    len2 = len(list2)+1
    #Initialize the matrix & first column and row (which are all 0/Null)
    lcsmatrix = {}
    for i in range(0, len1):
        lcsmatrix[(i, 0)] = 0
    for j in range(0, len2):
        lcsmatrix[(0, j)] = 0
    #This helps us be able to tell what entry of the list goes with each row/column of the matrix.
    rowindex = [0] + list1
    colindex = [0] + list2
    #We use a bottom-up dynamic algorithm programming approach for the LCS problem, creating a matrix of subproblem answers.
    for i in range(1, len1):
        for j in range(1, len2):
            if rowindex[i] == colindex[j]: #if the associated values of the lists match
                lcsmatrix[(i,j)] = 1 + lcsmatrix[(i-1, j-1)]
            else: #when there isn't a match
                up = lcsmatrix[(i-1, j)]
                left = lcsmatrix[(i, j-1)]
                if  up > left:
                    lcsmatrix[(i,j)] = up
                else:
                    lcsmatrix[(i,j)] = left

    if lcsmatrix[(len1 - 1, len2 - 1)] < 0:
        print("There are no lines that are the same between the two files.")
    else:
        #We reconstruct the solution, determining which lines are the same between the two files.
        #We start at the bottom right of the matrix and work back to the upper right.
        reconrow = len1 - 1
        reconcol = len2 - 1
        f1same = []
        f2same = []
        while (reconrow > 0) or (reconcol > 0): #We stop when we get to the upper right.
            if rowindex[reconrow] == colindex[reconcol]: #If there is a value match, these lines are the same and we save them.
                f1same.insert(0,reconrow)
                f2same.insert(0,reconcol)
                reconrow = reconrow - 1
                reconcol = reconcol - 1
            else: #There wasn't a line match so we continue on.
                up = lcsmatrix[(reconrow-1, reconcol)]
                left = lcsmatrix[(reconrow, reconcol -1)]
                if up > left:
                    reconrow = reconrow - 1
                else:
                    reconcol = reconcol - 1
        print(f1same)
        print(f2same)

diff()
