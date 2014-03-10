'''
Created on Jan 13, 2014

@author: artreven
'''
import copy

import fca
import rc.discrete_function, rc.ae
df = rc.discrete_function

def read_cxts():
    path_f2 = '/home/artreven/Dropbox/personal/Scripts/AptanaWorkspace/relational_clones/comm_funcs/f2.csv'
    path_f3a = '/home/artreven/Dropbox/personal/Scripts/AptanaWorkspace/relational_clones/comm_funcs/f3a.csv'
    path_fdanilchenko = '/home/artreven/Dropbox/personal/Scripts/AptanaWorkspace/relational_clones/comm_funcs/fdanilchenko.csv'
    cxt_f2 = fca.read_csv(path_f2)
    cxt_f3a = fca.read_csv(path_f3a) 
    cxt_fdanilchenko = fca.read_csv(path_fdanilchenko)
    
dest = '../ae_2valdomain2/'
f10 = df.DiscreteFunction(range(2), {(0,): 0, (1,): 0})
f11 = df.DiscreteFunction(range(2), {(0,): 0, (1,): 1})
f12 = df.DiscreteFunction(range(2), {(0,): 1, (1,): 0})
f13 = df.DiscreteFunction(range(2), {(0,): 1, (1,): 1})
f_t105 = df.DiscreteFunction(range(2), {(0,0,0): 0, (0,0,1): 1, (0,1,0): 1, (0,1,1): 0,
                                        (1,0,0): 1, (1,0,1): 0, (1,1,0): 0, (1,1,1): 1})
funcs = [f10, f11, f12, f13]#, f_t105]
table = [map(lambda x: df.commute(f, x) == True, funcs) for f in funcs]
cxt = fca.Context(table, map(str, funcs), map(str, funcs))

if __name__ == '__main__':
    ae = rc.ae.AE(cxt, dest, rc.ae.ce_finder, rc.ae.has_attribute, rc.ae.go_on)
    dict_wait = {'wait': 0.3}
    ae.run(find_ces=dict_wait, no_ces=dict_wait)