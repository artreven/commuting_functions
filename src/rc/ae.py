'''
Created on Feb 5, 2014

@author: artreven
'''
import os
import time
import shutil
import copy
import logging
from collections import defaultdict

import fca
import fca.readwrite.cxt

class AE(object):
    '''
    Class to represent Attribute Exploration procedure
    '''

    def __init__(self, cxt, dest, ce_finder, has_attribute, go_on=None):
        '''
        Constructor
        
        @param cxt: initial cxt to start with
        @param dest: proposed destination for current AE. May be changed if 
        already exists.
        @param ce_finder: should output dictionary {implication: counter-example}.
        Every counter example should have method has_attribute accepting attributes
        from the context.
        @param prover: should output (proved, not_proved)
        @param has_attribute: function taking CE and attribute and return boolean value
        @ivar proved: proved implications from current basis
        @ivar not proved: not proved yet implications from current basis
        @ivar step: current step of AE
        @ivar resistant_imps: dict with keys = premises, values = (conclusion, time restriction)
        '''
        ###Only for this time, redesign for general use
        self.resistant_ints = defaultdict(int)
        
        self.cxt = cxt
        self.proved = []
        self.not_proved = []
        self.resistant_imps = defaultdict(lambda: defaultdict(int))
        self.dest = def_dest(dest)
        self.go_on = go_on
        self.used = set(map(str, cxt.objects))
        self.ce_finder = ce_finder # usage *ce_finder(self.not_proved, self.dest, wait)*
        self.has_attribute = has_attribute
        logging.basicConfig(filename=dest + '/progress.log',
                            filemode='w',
                            format='%(levelname)s %(asctime)s: %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        self.step = 1
        # Create directories for proofs and counter-examples
        if os.path.exists(self.dest + '/proofs'):
            shutil.rmtree(self.dest + '/proofs')
        os.makedirs(self.dest + '/proofs')
        if os.path.exists(self.dest + '/ces'):
            shutil.rmtree(self.dest + '/ces')
        os.makedirs(self.dest + '/ces')
        
    def find_basis(self):
        """
        Find implication basis and save it in self.basis in unit form
        """
        ts = time.time()
        basis = self.cxt.get_aibasis()
        te = time.time()
        m = '\nIt took {0} seconds to compute the canonical basis.\n'.format(te-ts)
        self.logger.info(m)
        unit_basis = []
        for imp in basis:
            for j in (imp.conclusion - imp.premise):
                unit_basis.append(fca.Implication(imp.premise, set((j,))))
        self.not_proved = copy.deepcopy(unit_basis)
        self.proved = []
        return unit_basis
            
    def _delete_ces(self):
        """
        Delete all files output by ce_finder
        """
        for i in os.listdir(self.dest + '/ces'):
            os.remove(self.dest + '/ces/' + i)
                
    def _delete_proofs(self):
        """
        Delete all files output by prover
        """
        for i in os.listdir(self.dest + '/proofs'):
            os.remove(self.dest + '/proofs/' + i)
                
    def _clear_directory(self):
        self._delete_ces()
        self._delete_proofs()
        
    def _output_imps(self):
        with open(self.dest + '/proved.txt', 'w') as f:
            f.write('Proved Implications:\n')
            for imp in self.proved:
                f.write(str(imp) + '\n')
        f.close()
        with open(self.dest + '/not_proved.txt', 'w') as f:
            f.write('Not Proved Implications:\n')
            if not self.not_proved:
                f.write('None\n')
            else:
                for imp in self.not_proved:
                    f.write(str(imp) + '\n')
        f.close()
        
    def _output_cxt(self):
        with open(self.dest + '/cxt.txt', 'w') as f:
            f.write(str(self.cxt) + '\n')
        fca.readwrite.cxt.write_cxt(self.cxt, self.dest + '/cxt.cxt')
        
    def add_object(self, row, object_name):
        self.cxt.add_object(row, object_name)
        if self.not_proved:
            self.not_proved = None
        if self.proved:
            self.proved = None
        
    def add_attribute(self, col, attr_name):
        self.cxt.add_attribute(col, attr_name)
        if self.not_proved:
            self.not_proved = None
        if self.proved:
            self.proved = None
        
    def no_ces_found(self, wait=float('inf')):
        """
        Do something if no counter-examples found.
        """
        if self.go_on == None:
            m = '\nDo not know how to continue.'
            self.logger.info(m)
            return {}
        no_objs = len(self.cxt.objects)
        ts = time.time()
        new_objects = self.go_on(self, wait)
        te = time.time()
        # messages
        m = '\n\tGO ON PHASE, wait = {0}:\n'.format(wait)
        m += 'It took {0} seconds\n'.format(te - ts)
        m += 'There were {0} objects before the start of this step\n'.format(no_objs)
        m += '{0} new objects found\n'.format(len(new_objects))
        m += '{0} objects left after reducing\n'.format(len(self.cxt.objects))
        self.logger.info(m)
        return new_objects
    
    def find_ces(self, wait=float('inf')):
        """
        Try to find counter-examples for every implication and add them to
        context if found.
        
        @param wait: tuple of time limits for self.ce_finder
        @var ce_dict: dictionary {implication: counter-example}.
        Every counter example should have method has_attribute accepting
        attributes from the context.
        """
        self._delete_ces()
        no_imps = len(self.not_proved)
        no_objs = len(self.cxt.objects)
        ts = time.time()
        ce_dict = {}
        cnt = 0
        for imp in self.not_proved:
            cnt += 1
            ts_ce = time.time()
            (unit_conclusion,) = frozenset(imp.conclusion)
            if (wait <= self.resistant_imps[frozenset(imp.premise)][unit_conclusion]):
                info = ('Tried before', time.time() - ts_ce)
                ce = None
            else:
                ce = self.ce_finder(imp, wait)
                if hasattr(ce, '__len__') and len(ce) == 2:
                    ce, reason = ce
                    # max_wait is needed if time constraint is decreased, so that most valuable survives
                    if reason == 'stop':
                        max_wait = float('inf')
                    else:
                        max_wait = max(wait, self.resistant_imps[frozenset(imp.premise)][unit_conclusion])
                    self.resistant_imps[frozenset(imp.premise)][unit_conclusion] = max_wait
                ce_dict[imp] = ce
                info = (ce, time.time() - ts_ce)
            
            with open(self.dest + '/step{0}ces.txt'.format(self.step), 'a') as f:
                f.write('\tCounter-examples:\n')
                m = str(imp) + '\n'
                if info[0] and not isinstance(info[0], str):
                    m += 'Found: ' + str(info[0])
                else:
                    m += str(info[0])
                m += '\nTime taken:{0}\n\n'.format(info[1])
                f.write(m)
            if ce:
                break
        te = time.time()
        _add_objects(set(ce_dict.values()), self)
        with open(self.dest + '/step{0}ces.txt'.format(self.step), 'a') as f:
            f.write('\n\n\n\t Context:\n' + str(self.cxt))
        self.step += 1
        # messages
        m = '\nCOUNTER-EXAMPLE FINDING PHASE, wait = {0}:\n'.format(wait)
        m += 'It took {0} seconds.\n'.format(te - ts)
        m += 'Total {0} unit implications, processed {1} unit implications.\n'.format(no_imps, cnt)
        m += 'There were {0} objects before the start of this step\n'.format(no_objs)
        m += 'There were {0} counter-examples found on this step\n'.format(len([x for x in ce_dict.values() if x != None]))
        m += '{0} Objects left after reducing\n'.format(len(self.cxt.objects))
        self.logger.info(m)
        return ce_dict
    
    def run(self, **kwargs):
        """
        Run Attribute Exploration procedure till no other counter-examples
        can be found. Try to prove, return proved and not proved implications.
        
        @param ce_wait: tuple of how long to wait for ces.
        @param prove_wait: tuple of how long to wait for proofs.
        """
        while True:
            self._output_cxt()
            self._output_imps()
            # try to find counter-examples
            ts = time.time()
            m = '\n\tSTARTING STEP {0}\n'.format(self.step)
            self.logger.info(m)
            self.find_basis()
            ce_dict = _if_arg(kwargs, 'find_ces', self.find_ces)
            # if no CE found try to go on
            if not any(ce_dict.values()):
                m = '\nNo counter-examples found, trying to go on\n'
                self.logger.info(m)
                new_objects = _if_arg(kwargs, 'no_ces', self.no_ces_found)
                m = '\nSTEP TIME: {0} sec\n'.format(time.time() - ts)
                self.logger.info(m)
                if any(new_objects):
                    m = '\nNew objects found, continue to next step\n'
                    self.logger.info(m)
                    continue
                else:
                    m = '\nNo new objects, exiting\n'
                    self.logger.info(m)
                    break
            else:
                m = '\nSTEP TIME: {0} sec\n'.format(time.time() - ts)
                self.logger.info(m)
    
def def_dest(dest):
    """
    Create a new directory or modify name (if exists) and create.
    """
    if os.path.exists(dest):
        raise Exception, 'Folder already exists.'
    elif not os.path.exists(dest):
        os.makedirs(dest)
        return dest
    
def _if_arg(dict_args, name, func):
    return func(**dict_args[name]) if (name in dict_args) else func()

def _add_objects(new_objects, ae):
    for new_object in new_objects:
        if new_object != None:
            # for the case of commuting functions ces are attributes as well
            col = map(lambda x: ae.has_attribute(new_object, x),
                      ae.cxt.objects)
            ae.add_attribute(col, str(new_object))
            row = map(lambda x: ae.has_attribute(new_object, x),
                      ae.cxt.attributes)
            ae.add_object(row, str(new_object))
    cxt = ae.cxt.reduce_objects()
    table = cxt._extract_subtable(cxt.objects)
    ae.cxt = fca.context.Context(table, cxt.objects, cxt.objects)

############### Specific functions for exploration of commuting functions
import rc.discrete_function
df = rc.discrete_function

def ce_finder(imp, wait=None, max_arity=4):
    """
    Find counter-example for a single imp.
    """
    ls_f_other = map(df.DiscreteFunction.read_from_str, imp.premise)
    f_not = df.DiscreteFunction.read_from_str(imp.conclusion.pop())
    timeout = False
    for arity in range(1, max_arity):
        f_initial = df.DiscreteFunction(f_not.domain, {}, arity)
        try:
            return df.commuting_functions_from_negative(f_initial, ls_f_other,
                                                        f_not, wait).next()
        except StopIteration:
            continue
        except df.TimeoutException:
            timeout = True
            continue
    if timeout:
        reason = 'timeout'
    else:
        reason = 'stop'
    return None, reason

def has_attribute(dfunc, att):
    if isinstance(att, str):
        dfunc_other = df.DiscreteFunction.read_from_str(att)
        result = df.commute(dfunc, dfunc_other)
        return True if result == True else False
    else:
        assert False
        
def go_on(ae, wait=None, max_arity=4):
    domain = df.DiscreteFunction.read_from_str(ae.cxt.objects[0]).domain
    dict_new_objects = {}
    dict_info = {}
    old_attributes = set(ae.cxt.attributes)
    sorted_concepts = sorted(ae.cxt.concepts,
                             key=lambda x: x.intent,
                             reverse=True)
    for c in sorted_concepts:
        ts_c = time.time()
        intent = c.intent
        t_intent = tuple(intent)
        if (wait <= ae.resistant_ints[t_intent]):
            dict_info[t_intent] = ('Tried before with same or bigger time constraint',
                                   time.time() - ts_c)
            continue
        fs_extent = map(df.DiscreteFunction.read_from_str, c.extent)
        if any(set(done_intent) > intent
               for done_intent in dict_new_objects.keys()):
            dict_info[t_intent] = ('Bigger intent done before',
                                   time.time() - ts_c)
            continue
        ls_f_other = map(df.DiscreteFunction.read_from_str, intent)
        ls_f_not = map(df.DiscreteFunction.read_from_str,
                       old_attributes - intent)
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
                    #timeout = True
                    break
                else:
                    useful = (f.self_commuting() and
                              not (fs_extent and 
                                   all((df.commute(f, f_other) == True)
                                       for f_other in fs_extent)))
            if useful:
                dict_new_objects[t_intent] = f
                break
        if not useful:
            f = None
            max_wait = max(wait, ae.resistant_imps[t_intent])
            ae.resistant_ints[t_intent] = max_wait
        dict_info[t_intent] = (f, time.time() - ts_c)
    
    new_objects = dict_new_objects.values()
    _add_objects(new_objects, ae)
    with open(ae.dest + '/step{0}new_objs.txt'.format(ae.step-1), 'w') as f:
        f.write('\tNew objects:\n')
        for int_, ce_t in dict_info.items():
            m = 'Intent: ' + str(int_) + '\n'
            if ce_t[0] and not isinstance(ce_t[0], str):
                m += 'Found: ' + str(ce_t[0])
            else:
                m += str(ce_t[0])
            m += '\nTime taken:{0}\n\n'.format(ce_t[1])
            f.write(m)
        f.write('\n\n\n\t Context:\n' + str(ae.cxt))
    return new_objects
    
########################################################
if __name__ == '__main__':
    pass
