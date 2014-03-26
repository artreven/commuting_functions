'''
Created on Jan 23, 2014

@author: artreven
'''
from functools import update_wrapper
from itertools import product
from collections import OrderedDict, defaultdict
import random
import re
import time

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
    def __str__(self):
        return self.message
        
class NotCommuteException(Exception):
    """
    Thrown when functions do not commute, and no extension possible
    """
    def __init__(self, matrix, f, f_other):
        self.f = f.copy()
        self.f_other = f_other
        self.matrix = matrix
        self.message = 'Functions do not commute on {0}.'.format(matrix)
    def __str__(self):
        return self.message
    
class MergeConflictException(Exception):
    def __str__(self):
        return "Key already in dictionary and has different value"
    
class NoOutputException(Exception):
    def __init__(self, val):
        self.message = 'No way to commute: function does no output {0} for any input.'.format(val)
    def __str__(self):
        return self.message

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
        assert all(len(input_) == arity for input_ in dict_f.keys() if input_)
        self._dict_f = dict_f
        self.arity = arity
        self.domain = domain
    
    def get_dict_f(self):
        return self._dict_f
    
    def set_dict_f(self, new_dict):
        self._dict_f = new_dict
    dict = property(get_dict_f, set_dict_f)
    
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
    
    def copy(self):
        return DiscreteFunction(self.domain, self.dict.copy(), self.arity)
    
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
def commute(func_row, func_col):
    """
    Check if two function commute. If not, return the input for *func_row* and 
    the output *value* of *func_col* where they do not conform,
    i.e. *func_row(out_row) != value*.
    """
    assert func_row.domain == func_col.domain
    domain = func_row.domain
    for input_ in _get_all_inputs(domain, func_row.arity, func_col.arity):
        result, out_row, value = _commute_on(func_row, func_col, input_)
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
                to_break = False
                while True:
                    try:
                        if ls_f_not and any(commute(f, f_not) == True for f_not in ls_f_not):
                            f = _try_backtrack(f, assignments)
                            to_break = True
                            continue
                        else:
                            break
                    except ArgError:
                        break
                if to_break:
                    break
                input_ts = f.dict.keys()
                result = close_all_commuting(f, ls_f_other,
                                             assignments,
                                             input_ts,
                                             new_input)
                if result == True:
                    continue
                elif result == False:
                    f = _try_backtrack(f, assignments)
                    break
            else:
                if (not ls_f_not) or all(commute(f, f_not) != True for f_not in ls_f_not):
                    print 'Found', elapsed
                    yield f
                f = _try_backtrack(f, assignments)
        else:
            raise TimeoutException(wait)
    
    assert all(f.domain == f_other.domain for f_other in ls_f_other)
    if not ls_f_other:
        ls_f_other = [DiscreteFunction(f.domain,
                                       dict(zip(map(lambda x: (x,), f.domain), f.domain)),
                                       arity=1),]
    if any(f_not in set(ls_f_other) for f_not in ls_f_not):
        return iter(())
    if not wait:
        wait = float('inf')
    if not all(f_other.is_total() for f_other in ls_f_other):
        raise Exception, 'Second argument has to be a list of TOTAL functions.'
    assignments = OrderedDict()
    
    return (new_f.copy()
            for pf in construct(f, ls_f_other, ls_f_not)
            for new_f in _all_total(pf))
            
def get_random_function(domain, arity):
    total_domain = _get_total_domain(domain, arity)
    dict_f = dict(zip(total_domain, [random.choice(domain)
                                     for _ in range(len(domain)**arity)]))
    return DiscreteFunction(domain, dict_f, arity)

##################################IN PROGRESS##################################
def commuting_functions_from_negative(f, ls_f_other, f_not, wait=float('inf')):
    """
    Iterator over all functions built from partial *f* and commuting with all
    (total) functions from *ls_f_other* and not commuting with *f_not*.
    
    @note: starts constructing from *f_not*.
    @note: uses *backtrack* function and *all_total* to totalize output.
    @param wait: time limit for search with each arity.
    """  
    assert all(f.domain == f_other.domain for f_other in ls_f_other)
    if not ls_f_other:
        ls_f_other = [DiscreteFunction(f.domain,
                                       dict(zip(map(lambda x: (x,), f.domain),
                                                f.domain)),
                                       arity=1),]
    if f_not in set(ls_f_other):
        raise StopIteration
    if not wait:
        wait = float('inf')
    if not all(f_other.is_total() for f_other in ls_f_other):
        raise Exception, 'Second argument has to be a list of TOTAL functions.'
    
    d_bindings = _get_bindings(f_not, f.arity)
    # binded inputs (b_inp) are the following: f_not(f(binded_inp)) = f(_input),
    # where f is new_func. holds for every binded_inp in binded_inputs_ls.
    ts = time.time()
    while d_bindings:
        new_f_input, new_f_binded_inputs_ls = d_bindings.popitem()
        domain = f.domain[:]
        basic_f = f.copy()
        while domain:
            # Pick up a value from domain and assign it to new_func(new_func_input)
            new_f_output = basic_f.dict[new_f_input] = domain.pop()
            try:
                closed_basic_f = get_closure_on_defined(basic_f, ls_f_other)
            except NotCommuteException:
                continue
                    
            if not new_f_output in f_not.inverse_dict:
                iter_f = (ans_f.copy()
                          for pf in construct_commuting(closed_basic_f, ls_f_other,
                                                        OrderedDict(), wait)
                          for ans_f in _all_total(pf))
                for ans_f in iter_f:
                    yield ans_f
                else:
                    continue
             
            f_not_binded_inputs = f_not.inverse_dict[new_f_output]
            # try to define output from any binded input so that it is not equal to f_not_input
            # then new_f and f_not will not commute
            s_noncom_defs = (set(_get_total_domain(f_not.domain[:], f_not.arity)) -
                             set(f_not_binded_inputs))
            if not s_noncom_defs:
                continue
            
            # Binded inputs are in fact vectors:= list of binded inputs
            for ls_binded_inps in new_f_binded_inputs_ls:
                binded_f = closed_basic_f.copy()
                binded_f_dict = binded_f.dict
                # binded_inp should be one of noncom_defs to not commute, but some values are already defined
                value_if_defined = lambda x: binded_f_dict[x] if x in binded_f_dict else None
                new_func_outs = [value_if_defined(i) for i in ls_binded_inps]
                s_def_to_not_commute = _match_ls(ls_binded_inps, new_func_outs,
                                                 s_noncom_defs)
                for binded_outs in s_def_to_not_commute:
                    elapsed = time.time()-ts 
                    if elapsed > wait:
                        raise TimeoutException(wait)
                    binded_f.dict.update(zip(ls_binded_inps, binded_outs))
                    try:
                        closed_binded_f = get_closure_on_defined(binded_f, ls_f_other)
                    except NotCommuteException:
                        continue
                    iter_f = (ans_f.copy()
                              for pf in construct_commuting(closed_binded_f,
                                                            ls_f_other,
                                                            OrderedDict(),
                                                            wait - elapsed)
                              for ans_f in _all_total(pf))
                    for ans_f in iter_f:
                        print 'Found', elapsed
                        yield ans_f
                    else:
                        continue

def construct_commuting(f, ls_f_other, assignments, wait=float('inf')):
    ts = time.time()
    old_fs = []
    while (time.time() - ts) < wait:
        for new_input in _get_total_domain(f.domain, f.arity):
            to_repeat = False
            while True:
                if not new_input in f.dict:
                    assignments[new_input] = f.domain[-1:0:-1]
                    f.dict[new_input] = f.domain[0]
                    old_fs.append(f.copy())
                try:
                    f = get_closure_on_defined(f, ls_f_other, new_input)
                except NotCommuteException: 
                    try:
                        f = old_fs.pop()
                    except IndexError:
                        raise StopIteration
                    to_repeat = True
                    f = _try_backtrack(f, assignments)
                    old_fs.append(f.copy())
                else:
                    break
            if to_repeat:
                break
        else:
            yield f
            f = _try_backtrack(f, assignments)
    else:
        raise TimeoutException(wait)
            
def get_closure_on_defined(f, ls_f_other, new=None):
    """
    Close wrt ls_f_other using inputs on which f is defined.
    
    @note: f remains not changed.
    """
    def get_new_closure_on(f, ls_f_other, new_inputs, new=None):
        input_ts = f.dict.keys()
        for f_other in ls_f_other:
            s_matrices = _get_inputs_with(f_other.arity, input_ts, new)
            for matrix in s_matrices:
                try:
                    if not _commute_on(f, f_other, matrix)[0]:
                        raise NotCommuteException(matrix, f, f_other)
                except ToDefError as e:
                    f.dict[e.input_] = e.value
                    new_inputs.add(e.input_)
        return f
    new_f = f.copy()
    new_inputs = set()
    new_f = get_new_closure_on(new_f, ls_f_other, new_inputs, new)
    while new_inputs:
        next_new = new_inputs.pop()
        new_f = get_new_closure_on(new_f, ls_f_other, new_inputs, next_new)
    return new_f

###################################AUX FUNCTIONS################################
def _match_ls(refs, ls, s_ls):
    """
    Pick up all elements from *s_ls* that match the pattern *ls* where *None* is
    a wildcard (joker). If there are duplicate elements in *refs* on the same 
    places in answer there should be duplicate elements as well.
    """
    ans = s_ls.copy()
    dict_duplicates = get_dict_duplicates(refs)
    for i in range(len(ls)):
        ls_el = ls[i]
        dupl_inds = dict_duplicates[refs[i]]
        if ls_el == None:
            old_ans = ans.copy()
            ans = set()
            values = {x[i] for x in old_ans}
            for val in values:
                ans |= set(filter(lambda x: all(x[j] == val for j in dupl_inds),
                                  old_ans))
            continue
        else:
            ans = set(filter(lambda x: all(x[j] == ls_el for j in dupl_inds),
                             ans))
    return ans

def get_dict_duplicates(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return tally
    
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

def _try_backtrack(f, assignments):
    try:
        return _backtrack(f, assignments)
    except KeyError:
        raise StopIteration

def _backtrack(df, assignments):
    while True:
        latest_input, values = assignments.popitem()
        dict_new = df.dict
        try:
            dict_new[latest_input] = values.pop()
        except IndexError:
            del dict_new[latest_input]
            df = DiscreteFunction(df.domain, dict_new, df.arity)
        else:
            assignments[latest_input] = values
            return DiscreteFunction(df.domain, dict_new, df.arity)
            
def _commute_on(func_row, func_col, input_):
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

def close_all_commuting(func_row, ls_func_col, assignments, input_ts, new=None):
    """
    Check if *func_row* and all *ls_func_col* commute and if it is
    possible to commute with all these functions. If any values
    are forced, assigns these values.
    
    @note: *func_row* is applied horizontally, *ls_func_col* vertically.
    """
    for func_col in ls_func_col:
        inputs = _get_inputs_with(func_col.arity, input_ts, new)
        for input_ in inputs:
            while True:
                try:
                    result, _, _ = _commute_on(func_row, func_col, input_)
                    break
                except ArgError as e:
                    input_new = e.input_
                    # save for future iterations and assign first value from domain
                    assignments[input_new] = func_row.domain[-1:0:-1]
                    func_row.dict[input_new] = func_row.domain[0]
                    #value_new = func_row.dict[input_new]
                    func_row = DiscreteFunction(func_row.domain, func_row.dict, func_row.arity)
                except ToDefError as e:
                    input_new = e.input_
                    value_new = e.value
                    # save for future iterations and assign first value from domain
                    assignments[input_new] = []
                    func_row.dict[input_new] = value_new
                    func_row = DiscreteFunction(func_row.domain, func_row.dict, func_row.arity)
            if not result:
                return False
    return True

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

###################################BIN################################
def old_commuting_functions_from_negative(f, ls_f_other, f_not, wait=float('inf')):
    """
    Iterator over all functions built from partial *f* and commuting with all
    (total) functions from *ls_f_other* and not commuting with *f_not*.
    
    @note: starts constructing from *f_not*.
    @note: uses *backtrack* function and *all_total* to totalize output.
    @param wait: time limit for search with each arity.
    """
    def construct(f, ls_f_other):
        while True:
            for new_input in _get_total_domain(f.domain, f.arity):
                input_ts = f.dict.keys()
                result = close_all_commuting(f, ls_f_other,
                                             assignments,
                                             input_ts,
                                             new_input)
                if result == True:
                    continue
                elif result == False:
                    f = _try_backtrack(f, assignments, used)
                    break
            else:
                print 'Found', elapsed
                yield f
                f = _try_backtrack(f, assignments, used)
    
    
    assert all(f.domain == f_other.domain for f_other in ls_f_other)
    if not ls_f_other:
        ls_f_other = [DiscreteFunction(f.domain,
                                       dict(zip(map(lambda x: (x,), f.domain),
                                                f.domain)),
                                       arity=1),]
    if f_not in set(ls_f_other):
        raise StopIteration
    if not wait:
        wait = float('inf')
    if not all(f_other.is_total() for f_other in ls_f_other):
        raise Exception, 'Second argument has to be a list of TOTAL functions.'
    
    d_bindings = _get_bindings(f_not, f.arity)
    # binded inputs (b_inp) are the following: f_not(f(binded_inp)) = f(_input),
    # where f is new_func. holds for every binded_inp in binded_inputs_ls.
    old_dict = f.dict.copy()
    ts = time.time()
    elapsed = 0            
    while d_bindings:
        if elapsed > wait:
            raise TimeoutException(wait)
        elapsed = time.time() - ts
        new_f_input, new_f_binded_inputs_ls = d_bindings.popitem()
        domain = f.domain[:]
        # Pick up a value from domain and assign it to new_func(new_func_input)
        while domain:
            new_f_output = f.dict[new_f_input] = domain.pop()
            assignments = OrderedDict()
            used = set()
            f = DiscreteFunction(f.domain, f.dict, f.arity)
            if not new_f_output in f_not.inverse_dict:
                iter_pf = construct(f, ls_f_other)
                try:
                    for pf in iter_pf:
                        iter_new_f = _all_total(pf)
                        for new_f in iter_new_f:
                            yield new_f
                except StopIteration:
                    pass
                finally:
                    f.dict = old_dict.copy()
                continue
             
            f_not_binded_inputs = f_not.inverse_dict[new_f_output]
            # try to define output from any binded input so that it is not equal to f_not_input
            # then new_f and f_not will not commute
            s_noncom_defs = (set(_get_total_domain(f_not.domain[:], f_not.arity)) -
                             set(f_not_binded_inputs)) 
            if not s_noncom_defs:
                continue
            
            # Binded inputs are in fact vectors:= list of binded inputs
            for ls_binded_inps in new_f_binded_inputs_ls:
                new_dict = f.dict.copy()
                # binded_inp should be one of noncom_defs to not commute, but some values are already defined
                value_if_defined = lambda x: new_dict[x] if x in new_dict else None
                new_func_outs = [value_if_defined(i) for i in ls_binded_inps]
                s_def_to_not_commute = _match_ls(ls_binded_inps, new_func_outs,
                                                 s_noncom_defs)
                
                for binded_outs in s_def_to_not_commute:
                    f.dict.update(zip(ls_binded_inps, binded_outs))
                    new_f = DiscreteFunction(f.domain, f.dict, f.arity)
                    assignments = OrderedDict()
                    used = set()
                    iter_pf = construct(new_f, ls_f_other)
                    try:
                        for pf in iter_pf:
                            iter_new_f = _all_total(pf)
                            for new_f in iter_new_f:
                                yield new_f
                    except StopIteration:
                        pass
                    finally:
                        f.dict = new_dict.copy()
    # if out of bindings
    #raise StopIteration 

def get_closure_on_outputs(key, val, d_bindings, f, f_other):
    # if ls_matrix is empty we can not get this output row => no consequence
    try:
        ls_matrix = map(tuple, d_bindings[key])
    except KeyError:
        print 'no matrix to get such f_other output: ', key
        yield f
        raise StopIteration
    # if ls_matrix is not empty, but ls_other_input is empty then there is no way
    # to get such corner => commutation not possible
    try:
        ls_other_input = f_other.inverse_dict[val]
    except KeyError:
        raise NoOutputException(val)
    
    for new_defs in defs_iterator(set(ls_matrix), set(ls_other_input)):
        try:
            f.dict = merge(f.dict, new_defs)
            yield f
        except MergeConflictException:
            continue

def defs_iterator(s_matrices, s_defs):
    ls_in_matrices = []
    to_multiply = []
    for matrix in s_matrices:
        s_allowed_defs = _match_ls(matrix,
                                   [None]*len(matrix),
                                   s_defs)
        ls_in_matrices.append(matrix)
        to_multiply.append(s_allowed_defs)
    assignments = product(*to_multiply)
    for assignment in assignments:
        mid_dict = dict(zip(ls_in_matrices, assignment))
        ans = dict()
        for key in mid_dict:
            ans.update( dict(zip(key, mid_dict[key])) )
        yield ans

def merge(d, d_other):
    """
    Update dict if no conflicts found, else raise Exception
    """
    d_ans = d.copy()
    for key, val in d_other.items():
        try:
            if d_ans[key] != val:
                raise MergeConflictException
        except KeyError:
            d_ans[key] = val
    return d_ans

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

def _commute_on_defined(func_row, func_col):
    """
    Check if *func_row* and *func_col* commute on defined inputs 
    (= on which func_row is defined).
    
    @note: *func_row* is applied horizontally, *ls_func_col* vertically.
    """
    input_ts = func_row.dict.keys()
    for input_ in product(input_ts, repeat=func_col.arity):
        result, _, _ = _commute_on(func_row, func_col, input_)
        if result:
            continue
        else:
            return False
    return True

def commuting_closure(f, ls_f_other):
    """
    For partially defined *f* get commuting closure which is all the value that
    are forced by commutation with *ls_f_other*.
    """
    closed_f = get_closure_on_defined(f, ls_f_other)
    it_f = construct_commuting(closed_f, ls_f_other, OrderedDict(), set())
    for ans_f in it_f:
        yield ans_f

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

##################################### M A I N ##################################        
if __name__ == '__main__':
    import cProfile
    
    #To check
    #     set(['f_3_3_7623079246341', 'f_3_1_21', 'f_3_1_3']) -> set(['f_3_3_7538621575365'])
    # Timeout both
    f = DiscreteFunction(range(3), dict(), 3)
    ls_f_other = map(DiscreteFunction.read_from_str, ['f_3_3_7623079246341', 'f_3_1_21', 'f_3_1_3'])
    f_not = DiscreteFunction.read_from_str('f_3_3_7538621575365')
    it_f = commuting_functions_from_negative(f, ls_f_other, f_not)
    ts = time.time()
    try:
        f = next(it_f)
    except StopIteration:
        print "hit StopIteration"
        print 'Time taken: ', time.time() - ts
    print f
    
    #     set(['f_3_1_21', 'f_3_2_18603', 'f_3_3_7570117242603']) -> set(['f_3_3_6088926820179'])
    # from_negative timeout, batch finished in 3 secs
    ls_f_other = map(DiscreteFunction.read_from_str, ['f_3_1_21', 'f_3_2_18603', 'f_3_3_7570117242603'])
    f_not = DiscreteFunction.read_from_str('f_3_3_6088926820179')
    f = DiscreteFunction(range(3), dict(), 3)
    it_f = commuting_functions_batch(f, ls_f_other, [f_not,])
    ts = time.time()
    try:
        f = next(it_f)
    except StopIteration:
        print "hit StopIteration"
        print 'Time taken: ', time.time() - ts
    f = DiscreteFunction(range(3), dict(), 3)
    it_f = commuting_functions_from_negative(f, ls_f_other, f_not)
    ts = time.time()
    try:
        f = next(it_f)
    except StopIteration:
        print "hit StopIteration"
        print 'Time taken: ', time.time() - ts
    
#     set(['f_3_2_9832', 'f_3_1_0', 'f_3_1_21', 'f_3_1_13']) -> set(['f_3_2_16389'])
    f = DiscreteFunction(range(3), dict(), 3)
    ls_f_other = map(DiscreteFunction.read_from_str, ['f_3_2_9832', 'f_3_1_0', 'f_3_1_21', 'f_3_1_13'])
    f_not = DiscreteFunction.read_from_str('f_3_2_16389')
    it_f = commuting_functions_from_negative(f, ls_f_other, f_not)
    ts = time.time()
    try:
        f = next(it_f)
    except StopIteration:
        print "hit StopIteration"
        print 'Time taken: ', time.time() - ts
    print f

    assert False
    
    ls_str_funcs = ['f_3_1_13', 'f_3_1_18', 'f_3_1_3', 'f_3_1_0', 
                    'f_3_3_5170638564018', 'f_3_1_8', 'f_3_1_26', 'f_3_1_21']
    premise = map(DiscreteFunction.read_from_str, ls_str_funcs)
    f_not = DiscreteFunction.read_from_str('f_3_2_19458')
    f_needed = DiscreteFunction.read_from_str('f_3_3_5170640158341')
    print f_needed.output_dict()
    print all(commute(f_needed, f_other) == True for f_other in premise)
    print commute(f_needed, f_not) != True
    
    new_f = DiscreteFunction(range(3), {}, 3)
    f = next(commuting_functions_from_negative(new_f, premise, f_not))
    print f
    print all(commute(f, f_other) == True for f_other in premise)
    print commute(f, f_not) != True
    #Found: f_3_3_5170640158341
    #Time taken:133.394649029

    #set(['f_3_1_0', 'f_3_1_21', 'f_3_2_2187', 'f_3_2_17496', 'f_3_1_18', 
    #'f_3_2_13122']) -> set(['f_3_2_3168'])    
    f = DiscreteFunction(range(3), dict(), 3)
    ls_f_other = map(DiscreteFunction.read_from_str, ['f_3_1_0', 'f_3_1_21',\
    'f_3_2_2187', 'f_3_2_17496', 'f_3_1_18', 'f_3_2_13122'])
    f_not = DiscreteFunction.read_from_str('f_3_2_3168')
    it_f = commuting_functions_from_negative(f, ls_f_other, f_not)
    cProfile.run('''try: f = next(it_f)
except StopIteration: print "hit StopIteration"''')
    print f
    
    f = DiscreteFunction(range(3), dict(), 3)
    ls_f_other = map(DiscreteFunction.read_from_str,
                     ['f_3_1_3', 'f_3_1_21', 'f_3_3_7570117242603'])
    f_not = DiscreteFunction.read_from_str('f_3_3_7538621575365')
    it_f = commuting_functions_from_negative(f, ls_f_other, f_not)
    cProfile.run('''try: f = next(it_f)
except StopIteration: print "hit StopIteration"''')
    print f