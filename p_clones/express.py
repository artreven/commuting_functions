'''
Created on Jun 9, 2014

@author: artreven
'''
from itertools import combinations, permutations

import discrete_function as df

def p_express(F, f, time_limit=None, size_limit=None):
    """
    Function makes a try to parametrically express a function *f* through
    functions *F*. If expression not found returns *None*.
    """
    f_arity = f.arity
    goal_arity = f_arity + 1
    goal_clause = _make_id_from_func(f)
    for f_base in F:
        diff_arity = f_base.arity - f_arity 
        if diff_arity >= 0:
            a_clause = _make_id_from_func(f_base)
            for w_clause in decreased_arity(a_clause, diff_arity):
                for w2_clause in permuted_args(w_clause):
                    if _equiv(w2_clause, goal_clause):
                        return a_clause.str
                
def decreased_arity(clause, diff):
    """
    Return iterator over new clauses derived from *clause* by identifying args.
    """
    # REWRITE!
    
    arity = clause.arity
    if diff == 0:
        return clause
    else:
        all_pairs = combinations(range(1, arity+1), 2)
        for pair in all_pairs:
            perm = range(1, pair[1]) + [pair[0]] + range(pair[1], arity)
            new_clause = permute_args(clause, perm)
            yield decreased_arity(new_clause, diff-1)
            
def permuted_args(clause):
    """
    Return iterator over new clauses derived from *clause* by permuting args.
    """
    arity = clause.arity
    all_perms = permutations(range(1, arity+1), arity)
    for perm in all_perms:
        new_clause = permute_args(clause, perm)
        yield new_clause
        

def _make_clause_w_id(f):
    domain = f.domain
    dict_id = dict(zip(map(lambda x: (x,), domain), domain))
    df_id = df.DiscreteFunction(domain, dict_id, 1)
    return equal(f, df_id)

def _equiv(cl1, cl2):
    assert cl1.arity == cl2.arity
    inputs = df._get_total_domain(cl1.domain, cl1.arity)
    return all( map(lambda x: cl1(x) == cl2(x), inputs) )

def _make_id_from_func(f):
    return_id = lambda x: f(x[:-1]) == x[-1]
    return_id.str = "(" + str(f) + " == f_id)"
    return_id.arity = f.arity + 1
    return_id.domain = f.domain
    return return_id
###############################################################################

def equal(f1, f2):
    """
    Create the identity *f1* == *f2*. The result takes values of arguments as
    input and returns True if holds, False otherwise.
    """
    def return_id(t_args):
        """
        @param t_args: list of variable evaluations
        """
        if len(t_args) != f1.arity + f2.arity:
            m = "Equality: "
            m += "Expected {0} arguments, got {1}".format(f1.arity + f2.arity,
                                                          len(t_args))
            raise Exception, m
        return f1(t_args[:f1.arity]) == f2(t_args[f1.arity:])
    
    return_id.str = "(" + str(f1) + " == " + str(f2) + ")"
    return_id.arity = f1.arity + f2.arity
    return_id.domain = f1.domain
    return return_id

def conjunction(cl1, cl2):
    """
    Create a new clause - conjunction of two clauses. An identity is a clause.
    """
    def return_cl(t_args):
        if len(t_args) != cl1.arity + cl2.arity:
            m = "Conjunction: "
            m += "Expected {0} arguments, got {1}".format(cl1.arity + cl2.arity,
                                                          len(t_args))
            raise Exception, m
        return cl1(t_args[:cl1.arity]) and cl2(t_args[cl1.arity:]) 
    
    return_cl.str = "(" + cl1.str + " CONJ " + cl2.str + ")"
    return_cl.arity = cl1.arity + cl2.arity
    return_cl.domain = cl1.domain
    return return_cl

def permute_args(cl, t_arg_places):
    """
    Takes clause *cl* and tuple of numbers *t_arg_places* and returns a new 
    clause resulting from permuting arguments of *cl* according to
    *t_arg_places*. The new clause has the same domain; the arity may change as
    some arguments may be identified.
    """
    new_arity = len(set(t_arg_places))
    if max(t_arg_places) > cl.arity or max(t_arg_places) != new_arity:
        m = "Incorrect permutation {0} for arity {1}".format(t_arg_places, cl.arity)
        raise Exception, m

    def return_cl(t_args):
        if len(t_args) != new_arity:
            m = "Identification of args: "
            m += "Expected {0} arguments, got {1}".format(new_arity,
                                                          len(t_args))
            raise Exception, m
        new_input = tuple([t_args[i-1] for i in t_arg_places])
        return cl(new_input)
    
    return_cl.str = "(" + cl.str + " PERM{0})".format(t_arg_places)
    return_cl.arity = new_arity
    return_cl.domain = cl.domain
    return return_cl

def quantify(cl, arg_place):
    """
    Existentially quantify argument on place *arg* of clause *cl*.
    """
    if arg_place > cl.arity:
        m = "Arg place {0} exceeds number of arguments {1}".format(arg_place,
                                                                   cl.arity)
        raise Exception, m
    new_arity = cl.arity - 1
    
    def return_cl(t_args):
        if len(t_args) != new_arity:
            m = "Quantification of arg: "
            m += "Expected {0} arguments, got {1}".format(new_arity,
                                                          len(t_args))
            raise Exception, m
        new_inputs = [t_args[:arg_place-1] + (i,) + t_args[arg_place-1:]
                      for i in cl.domain]
        return any(map(cl, new_inputs))
    
    return_cl.str = "(Ex{0} ".format(arg_place) + cl.str + ")"
    return_cl.arity = new_arity
    return_cl.domain = cl.domain
    return return_cl