def levenstein (input1: list, input2: list, equal_function = None):
    """
    This function simulates Levenstein algorithm for calculate the M.E.D between two list of elements
    I also require to input a function for defining the equation between to elements, in default, it is "="
    """
    n = len(input1)
    m = len(input2)
    
    if (n == 0 or m == 0):
        return [], []
    
    minDistance = [[[0, 'n'] for _ in range (m + 1)] for _ in range (n + 1)]
    for i in range (n + 1):
        minDistance[i][0][0] = i
    for j in range (m + 1):
        minDistance[0][j][0] = j
        
    for i in range (1, n + 1):
        for j in range (1, m + 1):
            #! Substitution
            compare = None
            if (equal_function):
                compare = equal_function(input1[i - 1], input2[j - 1])
            else:
                compare = (input1[i - 1] == input2[j - 1])
            
            if (compare):
                minDistance[i][j][0] = minDistance[i - 1][j - 1][0]
                minDistance[i][j][1]= 'd' #! Diag
            else:
                minDistance[i][j][0] = minDistance[i - 1][j - 1][0] + 2
                minDistance[i][j][1]= 'd'
            
            #! Deletion
            if (minDistance[i - 1][j][0] + 1 < minDistance[i][j][0]):
                minDistance[i][j][0] = minDistance[i - 1][j][0] + 1
                minDistance[i][j][1] = 'u' #! Up
            
            #! Insertion
            if (minDistance[i][j - 1][0] + 1 < minDistance[i][j][0]):
                minDistance[i][j][0] = minDistance[i][j - 1][0] + 1
                minDistance[i][j][1] = 'l' #! Left
         
    output1 = []
    output2 = []
    index1, index2 = n, m
    
    while (index1 > 0 and index2 > 0):
        if (minDistance[index1][index2][1] == 'u'):
            output1 = [input1[index1 - 1]] + output1
            output2 = ["*"] + output2
            index1 -= 1
        
        elif (minDistance[index1][index2][1] == 'l'):
            output1 = ["*"] + output1
            output2 = [input2[index2 - 1]] + output2
            index2 -= 1
        
        elif (minDistance[index1][index2][1] == 'd'):
            output1 = [input1[index1 - 1]] + output1
            output2 = [input2[index2 - 1]] + output2
            index1 -= 1
            index2 -= 1
            
    while (index1 > 0):
        output1 = [input1[index1 - 1]] + output1
        output2 = ["*"] + output2
        index1 -= 1
    
    while (index2 > 0):
        output1 = ["*"] + output1
        output2 = [input2[index2 - 1]] + output2
        index2 -= 1
        
    return output1, output2