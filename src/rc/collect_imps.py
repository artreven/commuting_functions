'''
Created on Apr 10, 2014

@author: artreven
'''
from itertools import islice
import fca
import discrete_function as df

path_other_imps = '../not_done_imps'

def read_imps(path_to_file):
    ls_imps = []
    with open(path_to_file, 'r') as f:
        for line in f:
            if '->' in line:
                premise, conclusion = line.split('->')
                premise = eval(premise)
                conclusion = eval(conclusion)
                imp = fca.Implication(premise, conclusion)
                print imp
                ls_imps.append(imp)
    return ls_imps

if __name__ == '__main__':
    ls_imps = read_imps(path_other_imps)
    print len(ls_imps)