'''
Created on Jan 13, 2014

@author: artreven
'''
import threading
import time

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

def try_prove(finished, ls_f_other, f_not, wait, iter_creator, path_prog, stop_signal):
    f_initial = df.DiscreteFunction(range(3), {}, arity=3) 
    ts = time.time()
    try:
        next(iter_creator(f_initial, ls_f_other, f_not, wait, stop_signal))
        assert False
    except df.TimeoutException, df.StopSignalException:
        finished = False
        return False
    except StopIteration:
        stop_signal.set()
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
        finished = False
        cnt += 1
        with open(path_prog, 'a') as f:
            f.write('\n\n\n\tImplication number {0}:\n'.format(cnt))
            m = str(unit_imp.premise) + " -> " + str(unit_imp.conclusion) + '\n'
            f.write(m)
            
        ls_f_other = map(df.DiscreteFunction.read_from_str, unit_imp.premise)
        f_not = df.DiscreteFunction.read_from_str(unit_imp.conclusion.pop())
        iter_creator = df.commuting_functions_from_negative
        if not try_prove(finished, ls_f_other, f_not, wait, iter_creator, path_prog):
            iter_creator = df.commuting_functions_batch
            ls_f_not = [f_not,]
            if try_prove(ls_f_other, ls_f_not, wait, iter_creator, path_prog):
                proved.add(unit_imp)
                not_proved.remove(unit_imp)
        else:
            proved.add(unit_imp)
            not_proved.remove(unit_imp)
                       
def parallel_check(s_imps, wait, step=1):
    path_prog = './progress{0}.txt'.format(step)
    with open(path_prog, 'a') as f:
        f.write('\tNumber of implications to check: {0}\n\n'.format(len(s_imps)))
    cnt = 0
    signal = threading.Event()
    for unit_imp in s_imps:
        cnt += 1
        with open(path_prog, 'a') as f:
            f.write('\n\n\n\tImplication number {0}:\n'.format(cnt))
            m = str(unit_imp.premise) + " -> " + str(unit_imp.conclusion) + '\n'
            f.write(m)
        
        ls_f_other = map(df.DiscreteFunction.read_from_str, unit_imp.premise)
        f_not = df.DiscreteFunction.read_from_str(unit_imp.conclusion.pop())
        ls_f_not = [f_not,]
        finished = False
        t_batch = threading.Thread(target=try_prove,
                                   args=(finished, ls_f_other, ls_f_not, wait,
                                         df.commuting_functions_batch,
                                         path_prog, signal))
        t_neg = threading.Thread(target=try_prove,
                                 args=(finished, ls_f_other, f_not, wait,
                                       df.commuting_functions_from_negative,
                                       path_prog, signal))
        t_neg.start()
        t_batch.start()
        t_neg.join()
        t_batch.join()
        signal.clear()

# path_to_cxt = 'my_cxt.cxt'
# dest = '../ae_2valdomain_addbyone232/'
# f_2_1_0 = df.DiscreteFunction.read_from_str('f_2_1_0')
# f_2_1_2 = df.DiscreteFunction.read_from_str('f_2_1_2')
# f_2_2_14 = df.DiscreteFunction.read_from_str('f_2_2_14')
# f_2_3_150 = df.DiscreteFunction.read_from_str('f_2_3_150')
# f_2_3_232 = df.DiscreteFunction.read_from_str('f_2_3_232')
# funcs = [f_2_1_0, f_2_1_2, f_2_3_232]#, f_2_3_150]#, f_2_3_232]#, f13]
# table = [map(lambda x: df.commute(f, x) == True, funcs) for f in funcs]
# cxt = fca.Context(table, map(str, funcs), map(str, funcs))

if __name__ == '__main__':
    import time
    from collect_imps import read_imps
     
#     cxt = fca.readwrite.read_cxt(path_to_cxt)
#     basis = cxt.get_aibasis()
#     unit_basis = []
#     for imp in basis[:10]:
#         for j in (imp.conclusion - imp.premise):
#             unit_basis.append(fca.Implication(imp.premise, set((j,))))
               
    ls_imps = read_imps('./not_done_imps')
    s_imps = set(ls_imps)
    not_proved = set(s_imps)
    proved = set()
    parallel_check(s_imps=s_imps, wait=None, step=33)
    print 'done'

    
#     ae = rc.ae.AE(cxt, dest, rc.ae.ce_finder, rc.ae.has_attribute, rc.ae.go_on)
#     dict_wait50 = {'wait': 50}
#     dict_wait150 = {'wait': 150}
#     dict_wait10 = {'wait': 10}
#     ae.run(find_ces=dict_wait10, no_ces=dict_wait10)
