'''
Created on Mar 2, 2014

@author: artreven
'''
from collections import defaultdict, OrderedDict
from itertools import product

import rc.discrete_function
df = rc.discrete_function

class SymbolicFunction(object):
    '''
    classdocs
    '''


    def __init__(self, bindings):
        '''
        Constructor
        '''
        self._bindings = bindings
        
def prover(premise, f_not, arity):
    """
    Prove that implication 'from premise follows conclusion' holds, where
    premise and conclusion consist of discrete function and commuting is
    meant as relation.
    """
    d_bindings = _get_bindings(f_not, arity)
    # binded inputs (b_inp) are the following: f(x(b_inp)) = x(new_func_input),
    # where x is new_func. holds for every b_inp in binded_inputs_ls.
    # TODO: choose binding wisely (maybe, longest)
    while d_bindings:
        new_func_input, new_func_binded_inputs_ls = d_bindings.popitem()
        new_func_dict = dict()
        domain = f_not.domain[:]
        print
        print 'len(d_bindings)', len(d_bindings)
        # Pick up a value from domain and assign it to new_func(new_func_input)
        while domain:
            new_func_output = new_func_dict[new_func_input] = domain.pop()
            print 'new_func_output', new_func_output, domain
            if not new_func_output in f_not.inverse_dict:
                new_inp = new_func_input
                noncom_dict = new_func_dict.copy()
                while True:
                    noncom_func = df.DiscreteFunction(f_not.domain[:], 
                                                      noncom_dict,
                                                      arity)
                    assignments = dict()
                    res, out_row, out_val = df._commute_on_new_with_all(noncom_func,
                                                                        premise, new_inp,
                                                                        assignments)
                    if res == True:
                        it_f = df.commuting_functions_batch(noncom_func, premise, [])
                        return (f for f in it_f)
                    elif res == False:
                        print 'res == false'
                        break
                    elif res == None:
                        if not out_row in noncom_dict:
                            noncom_dict[out_row] = out_val
                        else:
                            break
                continue
            f_not_binded_inputs = f_not.inverse_dict[new_func_output]
            # try to define output from any binded input so that it is not equal to f_not_input
            # then new_func and f_not will not commute
            s_noncom_defs = (set(df._get_total_domain(f_not.domain[:], f_not.arity)) -
                             set(f_not_binded_inputs)) 
            if not s_noncom_defs:
                # TODO: try next value for new_func_output
                assert False
            # Binded inputs are in fact vectors:= list of binded inputs
            for new_func_ls_binded_inp in new_func_binded_inputs_ls:
                noncom_dict = new_func_dict.copy()
                # binded_inp should be one of noncom_defs to not commute, but some values are already defined
                value_if_defined = lambda x: new_func_dict[x] if x in new_func_dict else None
                new_func_outs = [value_if_defined(i) for i in new_func_ls_binded_inp]
                defs_to_not_commute = match_ls(new_func_outs, s_noncom_defs)
                while defs_to_not_commute:
                    assignment = defs_to_not_commute.pop()
                    for i in xrange(len(new_func_ls_binded_inp)):
                        go_on = False
                        if new_func_outs[i] != None:
                            continue
                        else:
                            new_inp = new_func_ls_binded_inp[i]
                            noncom_dict[new_inp] = assignment[i]
                            while True:
                                noncom_func = df.DiscreteFunction(f_not.domain[:], 
                                                                  noncom_dict,
                                                                  arity)
                                assignments = dict()
                                res, out_row, out_val = df._commute_on_new_with_all(noncom_func,
                                                                                    premise, new_inp,
                                                                                    assignments)
                                if res == True:
                                    go_on = True
                                    break
                                elif res == False:
                                    print 'res = flase 2'
                                    break
                                elif res == None:
                                    if not out_row in noncom_dict:
                                        noncom_dict[out_row] = out_val
                                    else:
                                        print 'res = None'
                                        break
                        if go_on:
                            continue
                        else:
                            break
                    else:
                        return (f
                                for f in df._all_total(df.DiscreteFunction(f_not.domain,
                                                                           new_func_dict,
                                                                           arity)))
    raise StopIteration
    
def match_ls(ls, s_ls):       
    mid_ans = s_ls.copy()
    for i in range(len(ls)):
        ls_el = ls[i]
        if ls_el == None:
            continue
        mid_ans = filter(lambda x: x[i] == ls_el, mid_ans)
    return mid_ans
    
def _get_bindings(f, other_arity):
    """
    f(x(input)) == x(result)
    keys = results, values = inputs
    """ 
    d_bindings = dict()
    possible_results = product(f.inverse_dict.keys(), repeat=other_arity)
    for result in possible_results:
        possible_inputs = map(lambda x: zip(*x),
                              product(*[f.inverse_dict[i] for i in result]))
        d_bindings[result] = possible_inputs
    return d_bindings
        
    
###############################################################################
if __name__ == '__main__':
    import cProfile
    import timeit
    f_3_1_21 = df.DiscreteFunction.read_from_str('f_3_1_21')
    f_3_1_2 = df.DiscreteFunction.read_from_str('f_3_1_2')
    f_3_1_14 = df.DiscreteFunction.read_from_str('f_3_1_14')
    f_3_2_14 = df.DiscreteFunction.read_from_str('f_3_2_14')
    f_3_2_0 = df.DiscreteFunction.read_from_str('f_3_2_0')
    
    ls_f_other = map(lambda x: df.DiscreteFunction.read_from_str(x),
                     ['f_3_2_19458', 'f_3_1_3', 'f_3_1_0', 'f_3_1_13', 'f_3_1_21',
                      'f_3_1_26', 'f_3_1_18'])
    f_3_2_81 = df.DiscreteFunction.read_from_str('f_3_2_81')
    # answer: f_3_3_7625260079001
    
    f_3_2_16389 = df.DiscreteFunction.read_from_str('f_3_2_16389') 
    f_3_3_6354277129881 = df.DiscreteFunction.read_from_str('f_3_3_6354277129881')
    f_3_1_12 = df.DiscreteFunction.read_from_str('f_3_1_12')
    f_3_3_3812411301552 = df.DiscreteFunction.read_from_str('f_3_3_3812411301552')
    
    f_not = f_3_2_81
    it_f = prover(ls_f_other, f_not, 3)
    f = it_f.next()
    print 'f', f
    print 'commute with other', [df.commute(f, f_other) for f_other in ls_f_other]
    print 'not commute with f_not', df.commute(f, f_not)
    