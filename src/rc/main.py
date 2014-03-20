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

def try_prove(ls_f_other, f_not, wait, iter_creator, path_prog):
    f_initial = df.DiscreteFunction(range(3), {}, arity=3) 
    ts = time.time()
    try:
        next(iter_creator(f_initial, ls_f_other, f_not, wait))
        assert False
    except df.TimeoutException:
        finished = False
        return False
    except StopIteration:
        finished = True
        return True
    finally:
        write_progress(iter_creator, finished, time.time() - ts, path_prog)
        

def write_progress(iter_creator, finished, elapsed, path_prog):
    with open(path_prog, 'a') as f:
        m = 'Ran ' + iter_creator.__name__ + '\n'
        m += 'Finished: ' + str(finished) + ', Time taken: ' + str(elapsed) + '\n'
        if finished:
            m += 'Done!'
        f.write(m)
        
def main_check(s_imps, wait, not_proved, proved, step=1):
    path_prog = './progress{0}.txt'.format(step)
    with open(path_prog, 'a') as f:
        f.write('\tNumber of implications to check: {0}\n\n'.format(len(s_imps)))
    cnt = 0 
    for unit_imp in s_imps:
        cnt += 1
        with open(path_prog, 'a') as f:
            f.write('\n\n\n\tImplication number {0}:\n'.format(cnt))
            m = str(unit_imp.premise) + " -> " + str(unit_imp.conclusion) + '\n'
            f.write(m)
            
        ls_f_other = map(df.DiscreteFunction.read_from_str, unit_imp.premise)
        f_not = df.DiscreteFunction.read_from_str(unit_imp.conclusion.pop())
        iter_creator = df.commuting_functions_from_negative
        if not try_prove(ls_f_other, f_not, wait, iter_creator, path_prog):
            iter_creator = df.commuting_functions_batch
            ls_f_not = [f_not,]
            if try_prove(ls_f_other, ls_f_not, wait, iter_creator, path_prog):
                proved.add(unit_imp)
                not_proved.remove(unit_imp)
        else:
            proved.add(unit_imp)
            not_proved.remove(unit_imp)

if __name__ == '__main__':
    import time
    
    cxt = fca.readwrite.read_cxt(path_to_cxt)
    basis = cxt.get_aibasis()
    unit_basis = []
    for imp in basis:
        for j in (imp.conclusion - imp.premise):
            unit_basis.append(fca.Implication(imp.premise, set((j,))))
              
    not_proved = set(unit_basis)
    proved = set()
    main_check(s_imps=unit_basis, wait=100, not_proved=not_proved, proved=proved)
    print 'done'

    
#     ae = rc.ae.AE(cxt, dest, rc.ae.ce_finder, rc.ae.has_attribute, rc.ae.go_on)
#     dict_wait50 = {'wait': 50}
#     dict_wait150 = {'wait': 150}
#     dict_wait10 = {'wait': 10}
#     ae.run(find_ces=dict_wait10, no_ces=dict_wait10)
