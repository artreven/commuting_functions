'''
Created on Jan 23, 2014

@author: artreven
'''
from functools import update_wrapper
from itertools import product, permutations
from collections import OrderedDict, defaultdict
import random
import re
import time
import numpy as np

#######################DECORATORS##############################################
def decorator(d):
    """
    Make function d a decorator: d wraps a function fn.
    """
    def _d(fn):
        return update_wrapper(d(fn), fn)
    update_wrapper(_d, d)
    return _d

@decorator
def memo(f):
    """
    Decorator that caches the return value for each call to f(args).
    Then when called again with same args, we can just look it up.
    """
    cache = {}
    def _f(*args):
        try:
            return cache[args]
        except KeyError:
            cache[args] = result = f(*args)
            return result
        except TypeError:
            print 'TypeError'
            # some element of args can't be a dict key
            return f(*args)
    return _f

####################################EXCEPTIONS#################################
class ArgError(Exception):
    """
    Thrown when function is not defined for input values
    """
    def __init__(self, input_):
        self.input_ = input_
        self.message = 'For input {0} function is not defined'.format(input_)
    def __str__(self):
        return self.message
    
class ToDefError(ArgError):
    """
    Thrown when function is not defined for input values and correct value is known
    """
    def __init__(self, input_, value):
        self.input_ = input_
        self.value = value
        self.message = 'For input {0} function is not defined, '.format(input_)
        self.message += 'but should be {0}'.format(value)
    def __str__(self):
        return self.message
    
class TimeoutException(Exception):
    def __init__(self, wait):
        self.message = 'Waited {0} seconds, timed out.'.format(wait)

############################CLASS#########################
class DiscreteFunction(object):
    '''
    Class for discrete function. Domain = {0,..k}^n, n - arity, k, n \in N_0.
    Output \in domain. Total.
    '''
    def __init__(self, domain, dict_f={}, arity=None):
        '''
        Constructor
        '''
        if not arity:
            try:
                arity = len(dict_f.keys()[0])
            except IndexError:
                raise Exception, 'Either dict_f should be not empty or arity should be input.'
        # check same arity everywhere
        #assert all(len(input_) == arity for input_ in dict_f.keys() if input_)
        self._dict_f = dict_f
        self.arity = arity
        self.domain = domain
    
    def get_dict_f(self):
        return self._dict_f
    dict = property(get_dict_f)
    
    def __call__(self, args):
        try:
            return self._dict_f[args]
        except KeyError:
            raise ArgError(args)
    
    def __eq__(self, other):
        return isinstance(other, DiscreteFunction) and self.dict == other.dict
    
    def __str__(self):
        if not self.is_total():
            return self.output_dict()
        size_domain = self.domain[-1] + 1
        inputs = sorted(self.dict.keys())
        index = 0
        cnt = 0
        for inp in inputs:
            index += size_domain**cnt * self.dict[inp]
            cnt += 1
        out = "f_{0}_{1}_{2}".format(size_domain, self.arity, index)
        return out
        
    def output_dict(self):
        out = ''
        for key, value in self.dict.items():
            out += str(key) +': ' + str(value) +'\n'
        return out
    
    def __repr__(self):
        out = 'rc.discrete_function.DiscreteFunction'
        out += """(domain={self.domain!r}, dict_f={self.dict!r}, arity={self.arity!r})""".format(self=self)
        return out
    
    def __hash__(self):
        return self.__str__().__hash__()
        
    def is_total(self):
        total_domain = _get_total_domain(self.domain, self.arity)
        inputs = self.dict.keys()
        return all(i in inputs for i in total_domain)
    
    def self_commuting(self):
        return commute(self, self) == True
    
    def get_inverse_dict(self):
        if not hasattr(self, "_inverse_dict"):
            self._inverse_dict = defaultdict(list)
            for k, v in self.dict.items():
                self._inverse_dict[v].append(k)
        return self._inverse_dict
    inverse_dict = property(get_inverse_dict)
    
    @classmethod
    def read_from_dict(cls, str_):
        """
        Read function from string of inputs: outputs. Compatible with
        *output_dict*.
        """
        dict_f = {}
        lines = str_.split('\n')
        max_int = 0
        for line in lines: 
            if not ':' in line: continue
            inp_str, outp_str = line.split(':')
            inp = tuple(map(int, re.findall(r'\d', inp_str)))
            outp = int(re.findall(r'\d', outp_str)[0])
            max_int = max(max_int, max(max(inp), outp))
            dict_f[inp] = outp
        return cls(range(max_int+1), dict_f)
    
    @classmethod
    def read_from_str(cls, str_):
        """
        Read function from string containing domain, arity, and index number
        of this function wrt domain and arity.
        Expected input: *{name}_{domain}_{arity}_{index}_{whatever}*,
        example: *kgb_2_1_1_poo* is the second (starts from 0) unary (arity=1) 
        function on domain of [0,1] = range(2), i.e. *0: 1, 1: 0*.
        
        @note: Compatible with *__str__*.
        """
        (str_size_domain, str_arity, str_index) = str_.split("_")[1:4]
        size_domain = int(str_size_domain)
        domain = range(size_domain)
        arity = int(str_arity)
        index = int(str_index)
        inputs = sorted(list(_get_total_domain(domain, arity)))
        cnt = 0
        dict_f = {}
        for inp in inputs:
            dict_f[inp] = ((index) % (size_domain**(cnt+1))) / (size_domain**cnt)
            cnt += 1 
        return cls(domain, dict_f)
        
    
#######################PUBLIC FUNCTIONS########################################
def commute_on(func_row, func_col, input_):
    """
    Check if *func_row* and *func_col* commute on *input_* and output row
    of results of *func_col* and the value of *func_col* on the output column.
    
    @note: *func_row* is applied horizontally, *func_col* vertically.
    """
    # input = tuple(tuple,.. tuple)
    out_col = tuple(map(func_row, input_))
    transposed_input = zip(*input_)
    out_row = tuple(map(func_col, transposed_input))
    try:
        return (func_row(out_row) == func_col(out_col), out_row, func_col(out_col))
    except ArgError:
        raise ToDefError(out_row, func_col(out_col))

def commute(func_row, func_col):
    """
    Check if two function commute. If not, return the input for *func_row* and 
    the output *value* of *func_col* where they do not conform,
    i.e. *func_row(out_row) != value*.
    """
    assert func_row.domain == func_col.domain
    domain = func_row.domain
    for input_ in _get_all_inputs(domain, func_row.arity, func_col.arity):
        result, out_row, value = commute_on(func_row, func_col, input_)
        if not result:
            return out_row, value
    return True

def commuting_functions(f, ls_f_other, ls_f_not=[], wait=float('inf')):
    """
    Iterator over all functions built from partial *f* and commuting with all
    (total) functions from *ls_f_other* and not commuting with *f_not*.
    
    @note: uses *backtrack* function and *all_total* to totalize output.
    """
    if not wait:
        wait = float('inf')
    if not all(f_other.is_total() for f_other in ls_f_other):
        raise Exception, 'Second argument has to be a list of TOTAL functions.'
    assignments = OrderedDict()
    used = set()
    def construct(f, ls_f_other, ls_f_not):
        ts = time.time()
        elapsed = 0       
        while elapsed < wait:
            elapsed = time.time() - ts
            try:
                results = (commute(f, f_other) for f_other in ls_f_other)
                for result in results:
                    if result != True:
                        break
                else:
                    if (not ls_f_not) or all(commute(f, f_not) != True
                                             for f_not in ls_f_not):
                        yield f
                    try:
                        f = _backtrack(f, assignments, used)
                    except KeyError:
                        raise StopIteration
                    else:
                        continue
            except ArgError as e:
                input_new = e.input_
                dict_new = f.dict
                # save for future iterations and assign first value from domain
                assignments[input_new] = f.domain[-1:0:-1]
                dict_new[input_new] = f.domain[0]
                f = DiscreteFunction(f.domain, dict_new, f.arity)
            else:
                assert len(result) == 2
                input_, new_value = result
                dict_new = f.dict.copy()
                if ((input_, 'bound') in assignments or
                    not input_ in assignments or
                    not new_value in assignments[input_]):
                    try:
                        f = _backtrack(f, assignments, used)
                    except KeyError:
                        raise StopIteration
                    else:
                        continue
                old_value = dict_new[input_]
                dict_new[input_] = new_value
                if frozenset(dict_new.items()) in used:
                    try:
                        f = _backtrack(f, assignments, used)
                    except KeyError:
                        raise StopIteration
                    else:
                        continue
                f = DiscreteFunction(f.domain, dict_new, f.arity)
                latest_input, values = assignments.popitem()
                if (input_ == latest_input):
                    assignments[input_] = filter(lambda x: x != new_value,
                                                 values)
                else:
                    assignments[latest_input] = values
                    assignments[(input_, 'bound')] = (new_value, old_value)
                continue
        else:
            raise TimeoutException(wait)
    
    return (f
            for pf in construct(f, ls_f_other, ls_f_not)
            for f in _all_total(pf))

def commuting_functions_batch(f, ls_f_other, ls_f_not=[], wait=float('inf')):
    """
    Iterator over all functions built from partial *f* and commuting with all
    (total) functions from *ls_f_other* and not commuting with all *ls_f_not*.
    
    @note: uses *backtrack* function and *all_total* to totalize output.
    @param wait: time limit for search with each arity.
    """
    def construct(f, ls_f_other, ls_f_not):
        ts = time.time()
        elapsed = 0       
        while elapsed < wait:
            elapsed = time.time() - ts
            for new_input in _get_total_domain(f.domain, f.arity):
                while True:
                    try:
                        if ls_f_not and any(commute(f, f_not) == True for f_not in ls_f_not):
                            f = _try_backtrack(f, assignments, used)
                            continue
                        else:
                            break
                    except ArgError:
                        break
                input_ts = f.dict.keys()
                result, input_, new_value = close_all_commuting(f, ls_f_other,
                                                                assignments,
                                                                input_ts,
                                                                new_input)
                if result == True:
                    continue
                elif result == False:
                    f = _try_backtrack(f, assignments, used)
                    break
                elif result == None:
                    to_break = False
                    while True:
                        f = _pre_backtrack(f, input_, new_value, assignments, used)
                        result, input_, new_value = close_all_commuting(f, ls_f_other,
                                                                        assignments,
                                                                        f.dict.keys())
                        if result == True:
                            break
                        elif result == False:
                            to_break = True
                            break
                    if to_break:
                        break
            else:
                print 'Found', elapsed, f
                yield f
                f = _try_backtrack(f, assignments, used)
        else:
            raise TimeoutException(wait)
    
    assert all(f.domain == f_other.domain for f_other in ls_f_other)
    if not ls_f_other:
        ls_f_other = [DiscreteFunction(f.domain, dict(zip(map(lambda x: (x,), f.domain), f.domain)), arity=1),]
    if any(f_not in set(ls_f_other) for f_not in ls_f_not):
        return iter(())
    if not wait:
        wait = float('inf')
    if not all(f_other.is_total() for f_other in ls_f_other):
        raise Exception, 'Second argument has to be a list of TOTAL functions.'
    assignments = OrderedDict()
    used = set()
    
    return (f
            for pf in construct(f, ls_f_other, ls_f_not)
            for f in _all_total(pf))
            
def get_random_function(domain, arity):
    total_domain = _get_total_domain(domain, arity)
    dict_f = dict(zip(total_domain, [random.choice(domain)
                                     for _ in range(len(domain)**arity)]))
    return DiscreteFunction(domain, dict_f, arity) 
            
###################################AUX FUNCTIONS################################
def _backtrack(df, assignments, used=set()):
    while True:
        latest_input, values = assignments.popitem()
        dict_new = df.dict.copy()
        if latest_input[-1] == 'bound':
            #assert isinstance(values, tuple)
            used.add(frozenset(dict_new.items()))  
            dict_new[tuple(latest_input[0])] = values[1]
            df = DiscreteFunction(df.domain, dict_new, df.arity)
        else:
            #assert isinstance(values, list)
            if latest_input in dict_new:
                del dict_new[latest_input]
            try:
                dict_new[latest_input] = values.pop()
            except IndexError:
                df = DiscreteFunction(df.domain, dict_new, df.arity)
            else:
                assignments[latest_input] = values
                if used and frozenset(dict_new.items()) in used:
                    df = DiscreteFunction(df.domain, dict_new, df.arity)
                    continue
                return DiscreteFunction(df.domain, dict_new, df.arity)

def close_all_commuting(func_row, ls_func_col, assignments, input_ts, new=None):
    """
    Check if *func_row* and all *ls_func_col* commute and if it is
    possible to commute with all these functions. If any values
    are forced, assigns these values.
    
    @note: *func_row* is applied horizontally, *ls_func_col* vertically.
    """
    dict_row_val = dict()
    for func_col in ls_func_col:
        inputs = _get_inputs_with(func_col.arity, input_ts, new)
        for input_ in inputs:
            while True:
                try:
                    result, out_row, out_val = commute_on(func_row, func_col, input_)
                    break
                except ArgError as e:
                    input_new = e.input_
                    # save for future iterations and assign first value from domain
                    assignments[input_new] = func_row.domain[-1:0:-1]
                    func_row.dict[input_new] = func_row.domain[0]
                    value_new = func_row.dict[input_new]
                    func_row = DiscreteFunction(func_row.domain, func_row.dict, func_row.arity)
                except ToDefError as e:
                    input_new = e.input_
                    value_new = e.value
                    # save for future iterations and assign first value from domain
#                     assignments[input_new] = [x for x in func_row.domain if x != value_new]
                    assignments[input_new] = []
                    func_row.dict[input_new] = value_new
                    func_row = DiscreteFunction(func_row.domain, func_row.dict, func_row.arity)
            try:
                if dict_row_val[out_row] != out_val:
                    return (False, None, None)
            except KeyError:
                dict_row_val[out_row] = out_val
            if result:
                continue
            else:
                return (None, out_row, out_val)
    return (True, None, None)

def _commute_on_defined(func_row, func_col):
    """
    Check if *func_row* and *func_col* commute on defined inputs 
    (= on which func_row is defined).
    
    @note: *func_row* is applied horizontally, *ls_func_col* vertically.
    """
    input_ts = func_row.dict.keys()
    for input_ in product(input_ts, repeat=func_col.arity):
        result, _, _ = commute_on(func_row, func_col, input_)
        if result:
            continue
        else:
            return False
    return True

def _dict2func(dict_f):
    '''
    Make function from dict_f.
    '''
    def f(args):
        try:
            return dict_f[args]
        except KeyError:
            raise ArgError(args)
    return f

def _get_total_domain(domain, arity):
    """
    Return iterator over all elements of {0, .. domain}^arity.
    """
    return product(domain, repeat=arity)

def _get_all_inputs(domain, arity_row, arity_col):
    """
    Get all inputs to check if functions commute. Every input is matrix of size
    arity_row \times arity_col 
    """
    return product(_get_total_domain(domain, arity_row), repeat=arity_col)

def _get_inputs_with(arity_col, input_ts, new=None):
    """
    Get all inputs using values *input_ts* (and involving *new* if given) and 
    suitable for another function (given its arity).
    """
    if new == None:
        inputs = input_ts
        def_inputs = product(inputs, repeat=arity_col)
        return (x for x in def_inputs)
    else:
        s_inputs = set(input_ts)
        s_inputs.add(new)
        inputs = tuple(s_inputs)
        def_inputs = product(inputs, repeat=arity_col)
        return (x for x in def_inputs if new in x)

def _all_total(f):
    """
    Return iterator over all possible total extensions of (partial) *f*. If *f*
    is total, return it.
    """
    if f.is_total():
        yield f
    else:
        assignments = OrderedDict()
        while True:
            for input_ in _get_total_domain(f.domain, f.arity):
                try:
                    f(input_)
                except ArgError as e:
                    input_new = e.input_
                    dict_new = f.dict
                    # save for future iterations and assign first value from domain
                    assignments[input_new] = f.domain[-1:0:-1]
                    dict_new[input_new] = f.domain[0]
            f = DiscreteFunction(f.domain, dict_new, f.arity)
            yield f
            try:
                f = _backtrack(f, assignments)
            except KeyError:
                raise StopIteration
            
def _try_backtrack(f, assignments, used):
    try:
        return _backtrack(f, assignments, used)
    except KeyError:
        raise StopIteration

def _pre_backtrack(f, input_, new_value, assignments, used):
    dict_new = f.dict.copy()
    if ((input_, 'bound') in assignments or
        not input_ in assignments or
        not new_value in assignments[input_]):
            return _try_backtrack(f, assignments, used)
    old_value = dict_new[input_]
    dict_new[input_] = new_value
    if frozenset(dict_new.items()) in used:
        return _try_backtrack(f, assignments, used)
    latest_input, values = assignments.popitem()
    if (input_ == latest_input):
        assignments[input_] = filter(lambda x: x != new_value,
                                     values)
    else:
        assignments[latest_input] = values
        assignments[(input_, 'bound')] = (new_value, old_value)
    return DiscreteFunction(f.domain, dict_new, f.arity)

##################################### M A I N ##################################
def _print_assignments(assignments):
    print 'Assignments'
    for i,j in assignments.items():
        print i, j
    print 'end\n'
    
def count_iter(iter_):
    s = 0
    for f in iter_:
        s += 1
    print s
        
if __name__ == '__main__':    
    dict_f = {(0,0,1): 1, (1,1,0): 0}
    DF6 = DiscreteFunction(range(2), dict_f)
    dict_f = {(0,0): 1, (0,1): 0, (1,0): 0, (1,1): 0}
    DF2 = DiscreteFunction(range(2), dict_f)
    commuting_functions_batch(DF6, [DF2,]).next()
