'''
Created on May 30, 2014

@author: artreven
'''
import time
import multiprocessing as mp
import os

import fca
import auto_ae.ae as ae

import discrete_function as df
DiscreteFunction = df.DiscreteFunction

############### Constants
dest = '../etc/f3s'
max_arity=3

############### Specific functions for exploration of commuting functions
def launch(algo, f_initial, ls_f_other, f_not, mpq):
    try:
        df_ce = next(algo(f_initial, ls_f_other, f_not))
        ans = (df_ce, 'Success: ' + algo.__name__)
    except StopIteration:
        ans = (None, 'Possibilities exhausted: ' + algo.__name__)
    mpq.put(ans)

def ce_finder(imp, wait):
    """
    Find counter-example for a single imp.
    """
    ls_f_other = map(eval, imp.premise)
    
    for f_not in map(eval, imp.conclusion):
        for arity in range(1, max_arity+1):
            f_initial = df.DiscreteFunction(f_not.domain, {}, arity)
            mpq = mp.Queue()
            
            batch_ps = mp.Process(target=launch,
                                  args=(df.commuting_functions_batch,
                                        f_initial, ls_f_other, [f_not,], mpq))
            neg_ps = mp.Process(target=launch,
                                args=(df.commuting_functions_from_negative,
                                      f_initial, ls_f_other, f_not, mpq))
            batch_ps.start()
            neg_ps.start()
            ans = mpq.get()
            neg_ps.terminate()
            batch_ps.terminate()
            
            if ans[0] != None:
                break
        if ans[0] != None:
            break
    return ans

def has_attribute(obj_str, att_str):
    dfunc = eval(obj_str)
    dfunc_other = eval(att_str)
    result = df.commute(dfunc, dfunc_other)
    return True if result == True else False

def go_on(ae, wait):
    new_funcs = find_oa_extension(ae.cxt, ae.dest + '/step{0}new_objs.txt'.format(ae.step),
                                  wait) 
    return new_funcs, new_funcs
    
def find_oa_extension(cxt, report_dest, wait):
    domain = eval(cxt.objects[0]).domain
    old_attributes = set(cxt.attributes)
    sorted_concepts = sorted(cxt.concepts,
                             key=lambda x: x.intent,
                             reverse=True) # largest intent first
    dict_info = dict()
    dict_new_objects = dict()
    for c in sorted_concepts:
        ts_c = time.time()
        t_intent = tuple(c.intent)
        t_concept = (t_intent, tuple(c.extent))
        
        ###
#         if (wait <= ae.resistant_ints[t_intent]):
#             dict_info[t_concept] = ('Tried before with same or bigger time constraint')
#             continue
#         if any(set(done_intent) > c.intent
#                for done_intent in dict_new_objects.keys()):
#             dict_info[t_concept] = ('Bigger intent done before')
#             continue
        ###
        #fs_extent = map(df.DiscreteFunction.str2df, c.extent)
        ls_f_other = map(eval, c.intent)
        ls_f_not = map(eval, old_attributes - c.intent)
        
        for arity in range(1, max_arity):
            f_initial = df.DiscreteFunction(domain, {}, arity)
            iter_f = df.commuting_functions_batch(f_initial, ls_f_other, ls_f_not, wait)
            useful = False
            while not useful:
                try:
                    f = next(iter_f)
                except StopIteration:
                    break
                except df.TimeoutException:
                    break
                else:
                    lower_neighbor = (not (set(c.extent) <= set(c.intent)) and
                                      f.self_commuting())
                    upper_neighbor = (not f.self_commuting() and 
                                      (set(c.extent) <= set(c.intent)))
                    useful = lower_neighbor or upper_neighbor
            else:#if useful:
                dict_new_objects[t_intent] = f
                break
        if not useful:
            f = None
            #max_wait = max(wait, resistant_imps[t_intent])
            #resistant_ints[t_intent] = max_wait
        dict_info[t_concept] = (f, time.time() - ts_c)
        if useful:
            break
    new_funcs = dict_new_objects.values()
    with open(report_dest, 'w') as f:
        f.write('\tNew objects:\n')
        for concept, ce_t in dict_info.items():
            (int_, ext_) = concept
            m = 'Intent: ' + str(int_) + '\n'
            m += 'Extent: ' + str(ext_) + '\n'
            if ce_t[0] and not isinstance(ce_t[0], str):
                m += 'Found: ' + str(ce_t[0]) + '\tself commuting: ' + f.self_commuting()
            else:
                m += str(ce_t[0])
            m += '\nTime taken:{0}\n\n'.format(ce_t[1])
            f.write(m)
    return new_funcs

################ Init cxt
def init_cxt(funcs):
    obj_funcs = map(df.DiscreteFunction.str2df, list(funcs))
    table = [[df.commute(f_row, f_col) == True
              for f_row in obj_funcs]
             for f_col in obj_funcs]
    return fca.Context(table, map(repr, obj_funcs), map(repr, obj_funcs))
    

############################################
if __name__ == '__main__':
    test_dir = '../etc/test_run'
    funcs = ['f_3_1_0']
    cxt = init_cxt(funcs)
    ae_cfs = ae.AE(test_dir, cxt, has_attribute, ce_finder,
                   go_on, attributes_growing=True)
    ae_cfs.run(1000)
# #     cxt = fca.read_cxt('../etc/current_cxt.cxt')
# #     id_ls = read_ids('../utils/ids4.txt')
#     cxt = init_cxt(2, id_ls)
#     ae_cfs = ae.AE(dest, cxt, has_attribute, ce_finder, go_on, attributes_growing=True)
# #     step = raw_input('Input step number: ')
# #     ae_bunnies.step = int(step)
#     ae_bunnies.run(100, 1)