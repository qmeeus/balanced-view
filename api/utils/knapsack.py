import numpy as np

'''
------------------------------------------------
Use dynamic programming (DP) to solve 0/1 knapsack problem
Time complexity: O(nW), where n is number of items and W is capacity
------------------------------------------------
knapsack_dp(values,weights,n_items,capacity,return_all=False)
Input arguments:
  1. values: a list of numbers in either int or float, specifying the values of items
  2. weights: a list of int numbers specifying weights of items
  3. n_items: an int number indicating number of items
  4. capacity: an int number indicating the knapsack capacity
  5. return_all: whether return all info, defaulty is False (optional)
Return:
  1. picks: a list of numbers storing the positions of selected items
  2. max_val: maximum value (optional)
------------------------------------------------
'''
def knapsack_dp(values,weights,n_items,capacity,return_all=False):
    check_inputs(values,weights,n_items,capacity)

    table = np.zeros((n_items+1,capacity+1),dtype=np.float32)
    keep = np.zeros((n_items+1,capacity+1),dtype=np.float32)

    for i in range(1,n_items+1):
        for w in range(0,capacity+1):
            wi = weights[i-1] # weight of current item
            vi = values[i-1] # value of current item
            if (wi <= w) and (vi + table[i-1,w-wi] > table[i-1,w]):
                table[i,w] = vi + table[i-1,w-wi]
                keep[i,w] = 1
            else:
                table[i,w] = table[i-1,w]

    picks = []
    K = capacity

    for i in range(n_items,0,-1):
        if keep[i,K] == 1:
            picks.append(i)
            K -= weights[i-1]

    picks.sort()
    picks = [x-1 for x in picks] # change to 0-index
    iter
    if return_all:
        max_val = table[n_items,capacity]
        return picks,max_val
    return picks

def check_inputs(values,weights,n_items,capacity):
    # check variable type
    assert(isinstance(values,list))
    assert(isinstance(weights,list))
    assert(isinstance(n_items,int))
    assert(isinstance(capacity,int))
    # check value type
    assert(all(isinstance(val,int) or isinstance(val,float) for val in values))
    assert(all(isinstance(val,int) for val in weights))
    # check validity of value
    assert(all(val >= 0 for val in weights))
    assert(n_items > 0)
    assert(capacity > 0)

if __name__ == '__main__':

    values = [2,3,4]
    weights = [100,2,3]
    n_items = 3
    capacity = 3
    picks = knapsack_dp(values,weights,n_items,capacity)
    print(picks)


# <-- TODO: Fix this -->
# import numpy as np
# from typing import List, Union


# def knapsack_dp(values:List[Union[int,float]], weights:List[int], n_items:int, capacity:int, return_all:bool=False):
#     '''
#     ------------------------------------------------
#     Use dynamic programming (DP) to solve 0/1 knapsack problem
#     Time complexity: O(nW), where n is number of items and W is capacity
#     ------------------------------------------------
#     knapsack_dp(values,weights,n_items,capacity,return_all=False)
#     Input arguments:
#     1. values: a list of numbers in either int or float, specifying the values of items
#     2. weights: a list of int numbers specifying weights of items
#     3. n_items: an int number indicating number of items
#     4. capacity: an int number indicating the knapsack capacity
#     5. return_all: whether return all info, defaulty is False (optional)
#     Return:
#     1. picks: a list of numbers storing the positions of selected items
#     2. max_val: maximum value (optional)
#     ------------------------------------------------
#     '''

#     check_inputs(values,weights,n_items,capacity)
#     n_items = min(n_items, len(values))

#     table = np.zeros((n_items, capacity), dtype=np.float32)
#     keep = np.zeros((n_items, capacity), dtype=np.float32)

#     for i in range(1, n_items + 1):
#         for w in range(0, capacity + 1):
#             wi = weights[i - 1]  # weight of current item
#             vi = values[i - 1]  # value of current item
#             if (wi <= w) and (vi + table[i - 1, w - wi] > table[i - 1, w]):
#                 table[i, w] = vi + table[i - 1, w - wi]
#                 keep[i, w] = 1
#             else:
#                 table[i, w] = table[i - 1, w]

#     picks = []
#     K = capacity

#     for i in range(n_items, 0, -1):
#         if keep[i, K] == 1:
#             picks.append(i)
#             K -= weights[i - 1]

#     picks.sort()
#     picks = [x - 1 for x in picks] # change to 0-index

#     if return_all:
#         max_val = table[n_items, capacity]
#         return picks, max_val

#     return picks


# def check_inputs(values:List[Union[int,float]], weights:List[int], n_items:int, capacity:int):
    
#     check_type = lambda obj, cls: isinstance(obj, cls)
#     check_types = lambda obj, cls, dtype: (check_type(obj, cls) and all(check_type(x, dtype) for x in obj))
    
#     array_types = (list, np.ndarray)
#     int_types = (int, np.int32, np.int64)
#     float_types = (float, np.float32, np.float64)
#     assert check_types(values, array_types, (*int_types, *float_types)), "Values: List of ints or floats"
#     assert check_types(weights, array_types, int_types), "Weights: List of ints"
#     assert check_type(n_items, int_types), "n_items: int"
#     assert check_type(capacity, int_types), "capacity: int"

#     assert all(val >= 0 for val in weights)
#     assert len(values) == len(weights), "Values and Weights should have the same length"
#     assert min(weights) <= capacity, f"The minimum weight should be <= the capacity"


# if __name__ == '__main__':

#     # values = [2,3,4]
#     # weights = [1,2,3]

#     values = np.array([2,5,3], dtype=np.float32)
#     weights = np.array([100,3,4], dtype=np.int32)

#     n_items = 5
#     capacity = 10
#     picks = knapsack_dp(values,weights,n_items,capacity)
#     print(picks)
