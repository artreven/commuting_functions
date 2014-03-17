'''
Created on Jan 13, 2014

@author: artreven
'''
import copy

import fca
import fca.readwrite
import rc.discrete_function, rc.ae
df = rc.discrete_function

def read_cxts():
    path_f2 = '/home/artreven/Dropbox/personal/Scripts/AptanaWorkspace/relational_clones/comm_funcs/f2.csv'
    path_f3a = '/home/artreven/Dropbox/personal/Scripts/AptanaWorkspace/relational_clones/comm_funcs/f3a.csv'
    path_fdanilchenko = '/home/artreven/Dropbox/personal/Scripts/AptanaWorkspace/relational_clones/comm_funcs/fdanilchenko.csv'
    cxt_f2 = fca.read_csv(path_f2)
    cxt_f3a = fca.read_csv(path_f3a) 
    cxt_fdanilchenko = fca.read_csv(path_fdanilchenko)

path_to_cxt = 'my_cxt.cxt'
dest = '../../ae_3valdomain3_from_neg_50/'
#f10 = df.DiscreteFunction(range(2), {(0,): 0, (1,): 0})
#f11 = df.DiscreteFunction(range(2), {(0,): 0, (1,): 1})
#f12 = df.DiscreteFunction(range(2), {(0,): 1, (1,): 0})
#f13 = df.DiscreteFunction(range(2), {(0,): 1, (1,): 1})
#f_t105 = df.DiscreteFunction(range(2), {(0,0,0): 0, (0,0,1): 1, (0,1,0): 1, (0,1,1): 0,
#                                        (1,0,0): 1, (1,0,1): 0, (1,1,0): 0, (1,1,1): 1})
#funcs = [f10, f11, f12, f13]#, f_t105]
#table = [map(lambda x: df.commute(f, x) == True, funcs) for f in funcs]
#cxt = fca.Context(table, map(str, funcs), map(str, funcs))

if __name__ == '__main__':
    import logging
    import time
    cxt = fca.readwrite.read_cxt(path_to_cxt)
    
    basis = cxt.get_aibasis()
    unit_basis = []
    for imp in basis:
        ls_f_other = map(df.DiscreteFunction.read_from_str, imp.premise)
        for j in (imp.conclusion - imp.premise):
            f_not = df.DiscreteFunction.read_from_str(j)
            # arity == 3
            if f_not.arity == 3:
                # First batch   
                f_initial = df.DiscreteFunction(f_not.domain, {}, arity=3)          
                ts_ce = time.time()
                try:
                    next(df.commuting_functions_batch(f_initial, ls_f_other,
                                                      [f_not,], wait=150))
                    assert False
                except df.TimeoutException:
                    pass
                except StopIteration:
                    with open('./progress.txt', 'a') as f:
                        f.write('\tImplication:\n')
                        m = str(imp.premise) + " -> " + str(j) + '\n'
                        m += '\nTime taken:{0}\n\n'.format(time.time() - ts_ce)
                        f.write(m)
                    continue
                # If timeout try from negative
                f_initial = df.DiscreteFunction(f_not.domain, {}, arity=3)
                ts_ce = time.time()
                try:
                    next(df.commuting_functions_from_negative(f_initial,
                                                              ls_f_other,
                                                              f_not,
                                                              wait=150))
                    assert False
                except df.TimeoutException:
                    print "For {0} -> {1} time limit reached".format(map(str,
                                                                         ls_f_other),
                                                                     f_not)
                    assert False
                except StopIteration:
                    with open('./progress.txt', 'a') as f:
                        f.write('\tImplication:\n')
                        m = str(imp.premise) + " -> " + str(j) + '\n'
                        m += '\nTime taken:{0}\n\n'.format(time.time() - ts_ce)
                        f.write(m)
                    continue
            # if arity is less then 3
            elif f_not.arity < 3:
                # First from negative   
                f_initial = df.DiscreteFunction(f_not.domain, {}, arity=3)         
                ts_ce = time.time()
                try:
                    next(df.commuting_functions_from_negative(f_initial,
                                                              ls_f_other,
                                                              f_not,
                                                              wait=150))
                    assert False
                except df.TimeoutException:
                    pass
                except StopIteration:
                    with open('./progress.txt', 'a') as f:
                        f.write('\tImplication:\n')
                        m = str(imp.premise) + " -> " + str(j) + '\n'
                        m += '\nTime taken:{0}\n\n'.format(time.time() - ts_ce)
                        f.write(m)
                    continue
                # If timeout try from negative
                f_initial = df.DiscreteFunction(f_not.domain, {}, arity=3)
                ts_ce = time.time()
                try:
                    next(df.commuting_functions_batch(f_initial, ls_f_other,
                                                      [f_not,], wait=150))
                    assert False
                except df.TimeoutException:
                    print "For {0} -> {1} time limit reached".format(map(str,
                                                                         ls_f_other),
                                                                     f_not)
                    assert False
                except StopIteration:
                    with open('./progress.txt', 'a') as f:
                        f.write('\tImplication:\n')
                        m = str(imp.premise) + " -> " + str(j) + '\n'
                        m += '\nTime taken:{0}\n\n'.format(time.time() - ts_ce)
                        f.write(m)
                    continue
    print 'done'
#     ae = rc.ae.AE(cxt, dest, rc.ae.ce_finder, rc.ae.has_attribute, rc.ae.go_on)
#     dict_wait50 = {'wait': 50}
#     dict_wait150 = {'wait': 150}
#     dict_wait10 = {'wait': 10}
#     ae.run(find_ces=dict_wait10, no_ces=dict_wait10)
