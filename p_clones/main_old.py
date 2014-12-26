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
    except (df.TimeoutException, df.StopSignalException):
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
            m += 'Done!\n'
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
        finished1 = False
        finished2 = False
        t_batch = threading.Thread(target=try_prove,
                                   args=(finished1, ls_f_other, ls_f_not, wait,
                                         df.commuting_functions_batch,
                                         path_prog, signal))
        t_neg = threading.Thread(target=try_prove,
                                 args=(finished2, ls_f_other, f_not, wait,
                                       df.commuting_functions_from_negative,
                                       path_prog, signal))
        t_neg.start()
        t_batch.start()
        t_neg.join()
        t_batch.join()
        signal.clear()
        
def none_finder(*args):
    return None

path_to_cxt = 'my_cxt.cxt'
dest = '../ae_2valdomain_nocs/'
f_2_1_1 = df.DiscreteFunction.read_from_str('f_2_1_1')
f_2_1_2 = df.DiscreteFunction.read_from_str('f_2_1_2')
f_2_2_14 = df.DiscreteFunction.read_from_str('f_2_2_14')
f_2_3_150 = df.DiscreteFunction.read_from_str('f_2_3_150')
f_2_3_232 = df.DiscreteFunction.read_from_str('f_2_3_232')
funcs = [f_2_1_2]#, f_2_1_2, f_2_3_232]#, f_2_3_150]#, f_2_3_232]#, f13]
#table = [map(lambda x: df.commute(f, x) == True, funcs) for f in funcs]
#cxt = fca.Context(table, map(str, funcs), map(str, funcs))

if __name__ == '__main__':
    nonsc_cxt = fca.read_cxt('./not_self_commuting.cxt')
    full_cxt = fca.read_cxt('./my_cxt.cxt')
    full_funcs = map(df.DiscreteFunction.read_from_str, full_cxt.objects)
    noncom_funcs = map(df.DiscreteFunction.read_from_str, nonsc_cxt.objects)
    '''
    for obj in reversed(nonsc_cxt.objects):
        obj_intent = full_cxt.get_object_intent(obj)
        print '\n\nNonsc function ', obj
        print 'Commutes with: ', map(str, obj_intent)
        print 'length ', len(obj_intent)
        f_init = df.DiscreteFunction(range(3), {}, 3)
        premise = map(df.DiscreteFunction.read_from_str, obj_intent)
        conc = map(df.DiscreteFunction.read_from_str, set(full_cxt.objects) - set(obj_intent))
        print set(premise) & set(conc)
        print len(set(premise) | set(conc))
        try:
            for f in df.commuting_functions_batch(f_init, premise, conc):
                print 'Something found ', f
                if f.self_commuting():
                    break
            else:
                raise StopIteration
        except StopIteration:
            print 'Nothing found'
        except df.TimeoutException:
            print 'Timed out'
        else:
            f_int = [str_f_0 for str_f_0 in full_cxt.objects if df.commute(f, df.DiscreteFunction.read_from_str(str_f_0))]
            print 'found ', f
            print 'Commutes with: ', map(str, f_int)
            print 'length ', len(f_int)
    
    '''
    premise = ['f_3_1_0', 'f_3_1_12', 'f_3_1_13', 'f_3_1_21', 'f_3_1_26', 'f_3_2_9072', 'f_3_1_22']
    conc = 'f_3_2_16402'
    for obj in reversed(nonsc_cxt.objects):
        obj_intent = full_cxt.get_object_intent(obj)
        if set(premise) <= set(obj_intent) and not conc in obj_intent:
            print 'found', obj
    else:
        print 'none found'