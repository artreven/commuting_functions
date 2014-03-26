'''
Use with Nosetests (https://nose.readthedocs.org/en/latest/)

Created on Jan 24, 2014

@author: artreven
'''
from nose.tools import assert_raises, nottest  # @UnresolvedImport

import rc.discrete_function
df = rc.discrete_function

class Test:

    def setUp(self):
        dict_f = {}
        self.DF0 = df.DiscreteFunction(range(2), dict_f, 2)
        dict_f = {(0,0): 0, (0,1): 1, (1,0): 1, (1,1): 1}
        self.DF1 = df.DiscreteFunction(range(2), dict_f)
        dict_f = {(0,0): 1, (0,1): 0, (1,0): 0, (1,1): 0}
        self.DF2 = df.DiscreteFunction(range(2), dict_f)
        dict_f = {(0,0): 1, (0,1): 1, (1,0): 1, (1,1): 1}
        self.DF3 = df.DiscreteFunction(range(2), dict_f)
        dict_f = {(0,0): 0, (0,1): 0}
        self.DF4 = df.DiscreteFunction(range(2), dict_f)
        dict_f = {(0,0): 0, (1,1): 0}
        self.DF5 = df.DiscreteFunction(range(2), dict_f)
        dict_f = {(0,0,1): 1, (1,1,0): 0}
        self.DF6 = df.DiscreteFunction(range(2), dict_f)
        dict_f = {(0,0): 1, (0,1): 1, (1,0): 1, (1,1): 2,
                  (2,0): 2, (2,1): 2, (1,2): 2, (0,2): 2,
                  (2,2): 1}
        self.DF13 = df.DiscreteFunction(range(3), dict_f)
        self.DF03 = df.DiscreteFunction(range(3), {}, 2)

    def tearDown(self):
        pass

    @nottest
    def test_const_arity(self):
        dict_f = {(0,0): 0, (0,1): 0, (1,0): 1, (1,1,1): 1}
        assert_raises(AssertionError, df.DiscreteFunction, range(2), dict_f)
        
    def test_totality(self):
        dict_f = {(0,0): 0, (0,1): 0, (1,0): 1}
        assert not df.DiscreteFunction(range(2), dict_f).is_total()
        
    def test_commute_on(self):
        assert df._commute_on(self.DF1, self.DF2, ((0, 0), (1, 1)))[0]
        
    def test_not_commute_on(self):
        assert not df._commute_on(self.DF1, self.DF2, ((1, 0), (1, 0)))[0]
        
    def test_commute_stats(self):
        assert df._commute_on(self.DF1, self.DF2, ((1, 0), (1, 0))) == (False, (0,1), 0)
        
    def test_get_total_domain(self):
        assert (2,2) in df._get_total_domain(range(3), 2)
        assert (2,1) in df._get_total_domain(range(3), 2)
        assert (0,2) in df._get_total_domain(range(3), 2)
        assert (1,0) in df._get_total_domain(range(3), 2)
        assert not (3,2) in df._get_total_domain(range(3), 2)
        assert not (1,0,2) in df._get_total_domain(range(3), 2)
        
    def test_get_all_inputs(self):
        assert ((1,0), (2,2), (0,2)) in df._get_all_inputs(range(3), 2, 3)
        assert not ((1,0), (3,0), (0,0)) in df._get_all_inputs(range(3), 2, 3)
        assert len([1 for _ in df._get_all_inputs(range(3), 2, 3)]) == 729
        
    def test_not_commute(self):
        assert not (df.commute(self.DF1, self.DF2) == True)
   
    def test_commute(self):
        assert df.commute(self.DF3, self.DF3)

    def test_get_commuting_two_values_needed(self):
        assert df.commuting_functions_batch(self.DF4, [self.DF3,]).next()

    def test_no_commuting_function(self):
        assert_raises(StopIteration, next, df.commuting_functions_batch(self.DF5,
                                                                  [self.DF3,]))

    def test_ternary_commuting_function(self):
        assert df.commuting_functions_batch(self.DF6, [self.DF2,]).next()

    def test_count_commutting_function(self):
        it_f = df.commuting_functions_batch(self.DF03, [self.DF13,])
        s = 0
        while True:
            try:
                it_f.next()
                s += 1
            except StopIteration:
                break
        assert s > 1

    def test_no_commuting_noncommuting_function(self):
        it_f = df.commuting_functions_batch(self.DF03, [self.DF13,], [self.DF13,])
        assert_raises(StopIteration, next, it_f)

    def test_exist_commuting_functions_batch(self):
        dict_f = {(0,0): 0, (0,1): 1, (1,0): 1, (1,1): 2,
              (2,0): 2, (2,1): 2, (1,2): 2, (0,2): 2,
              (2,2): 0}
        f_other1 = df.DiscreteFunction(range(3), dict_f)
        dict_f = {(0,0): 1, (0,1): 0, (1,0): 0, (1,1): 1,
              (2,0): 0, (2,1): 0, (1,2): 1, (0,2): 1,
              (2,2): 0}
        f_other2 = df.DiscreteFunction(range(3), dict_f)
        ls_f_other = [f_other1, f_other2]
        it_f = df.commuting_functions_batch(df.DiscreteFunction(range(3), {}, 2),
                                      ls_f_other)
        assert it_f.next()
    
    def test_no_commuting_duplicates(self):
        dict_f = {(0,0): 0, (0,1): 0, (1,0): 0, (1,1): 0,
                  (2,0): 0, (2,1): 0, (1,2): 0, (0,2): 0,
                  (2,2): 0}
        f_other1 = df.DiscreteFunction(range(3), dict_f)
        dict_f = {(0,0): 1, (0,1): 1, (1,0): 1, (1,1): 1,
                  (2,0): 1, (2,1): 1, (1,2): 1, (0,2): 1,
                  (2,2): 1}
        f_other2 = df.DiscreteFunction(range(3), dict_f)
        ls_f_other = [f_other1, f_other2]
        it_f = df.commuting_functions_batch(df.DiscreteFunction(range(3), {}, 2),
                                            ls_f_other)
        ls_fs = list(it_f)
        for f in ls_fs:
            if ls_fs.count(f) > 1:
                print f
        s_fs = set(ls_fs)  
        print len(s_fs), len(ls_fs)
        assert len(s_fs) == len(ls_fs)
        

    def test_find_commuting_counterexample(self):
        dict_f = {(0,0): 0, (0,1): 0, (1,0): 0, (1,1): 0,
                  (2,0): 0, (2,1): 0, (1,2): 0, (0,2): 0,
                  (2,2): 0}
        f_other1 = df.DiscreteFunction(range(3), dict_f)
        dict_f = {(0,0): 1, (0,1): 1, (1,0): 1, (1,1): 1,
                  (2,0): 1, (2,1): 1, (1,2): 1, (0,2): 1,
                  (2,2): 1}
        f_other2 = df.DiscreteFunction(range(3), dict_f)
        ls_f_other = [f_other1, f_other2]
        dict_f = {(0,0): 1, (0,1): 0, (1,0): 0, (1,1): 1,
                  (2,0): 0, (2,1): 0, (1,2): 1, (0,2): 1,
                  (2,2): 0}
        f_other3 = df.DiscreteFunction(range(3), dict_f)
        it_f = df.commuting_functions_batch(df.DiscreteFunction(range(3), {}, 2),
                                      ls_f_other, [f_other3,])
        assert it_f.next()
        it_f = df.commuting_functions_from_negative(df.DiscreteFunction(range(3), {}, 2),
                                                    ls_f_other, f_other3)
        assert it_f.next()
        
        
    def test_find_from_noncommuting(self):
        dict_f = {(0,0): 1, (0,1): 0, (1,0): 0, (1,1): 1,
                  (2,0): 0, (2,1): 0, (1,2): 1, (0,2): 1,
                  (2,2): 0}
        f_other3 = df.DiscreteFunction(range(3), dict_f)
        it_f = df.commuting_functions(df.DiscreteFunction(range(3), {}, 2), [],
                                      [f_other3,])
        f = it_f.next()
        assert df.commute(f, f_other3) != True
        
    def test_totalize(self):
        dict_f = {(0,0): 1, (0,1): 0, (1,0): 0, (1,1): 1}
        f = df.DiscreteFunction(range(3), dict_f)
        f = df._all_total(f).next()
        assert f.is_total()
        
    def test_totalize_normal_stop(self):
        dict_f = {(0,0): 1, (0,1): 0, (1,0): 0, (1,1): 1}
        f = df.DiscreteFunction(range(3), dict_f)
        s = 0
        for f in df._all_total(f):
            s += 1
            assert f.is_total()
        assert s == 3**5
        
    def test_class_read(self):
        dict_f = {(0,0): 1, (0,1): 0, (1,0): 0, (1,1): 1}
        f = df.DiscreteFunction(range(2), dict_f)
        assert df.DiscreteFunction.read_from_str(str(f)) == f
        
    def test_from_neg1(self):
        f_other1 = df.DiscreteFunction.read_from_str('f_3_2_17496')
        f_other2 = df.DiscreteFunction.read_from_str('f_3_1_21')
        f_not = df.DiscreteFunction.read_from_str('f_3_1_18')
        premise = [f_other1, f_other2]
        new_f = df.DiscreteFunction(range(3), {}, 3)
        assert_raises(StopIteration, next,
                      df.commuting_functions_from_negative(new_f, premise, f_not))
    
 
    def test_from_neg2(self):
        f_other1 = df.DiscreteFunction.read_from_str('f_3_2_17496')
        f_other2 = df.DiscreteFunction.read_from_str('f_3_1_21')
        f_not = df.DiscreteFunction.read_from_str('f_3_2_13122')
        premise = [f_other1, f_other2]
        new_f = df.DiscreteFunction(range(3), {}, 3)
        assert_raises(StopIteration, next,
                      df.commuting_functions_from_negative(new_f, premise, f_not))
     
  
    def test_from_neg3(self):
        f_other1 = df.DiscreteFunction.read_from_str('f_3_1_8')
        f_other2 = df.DiscreteFunction.read_from_str('f_3_1_21')
        f_not = df.DiscreteFunction.read_from_str('f_3_1_18')
        premise = [f_other1, f_other2]
        new_f = df.DiscreteFunction(range(3), {}, 3)
        assert_raises(StopIteration, next,
                      df.commuting_functions_from_negative(new_f, premise, f_not))
        
    def test_from_neg_finds(self):
        ls_str_funcs = ['f_3_1_13', 'f_3_1_18', 'f_3_1_3', 'f_3_1_0', 
                'f_3_3_5170638564018', 'f_3_1_8', 'f_3_1_26', 'f_3_1_21']
        premise = map(df.DiscreteFunction.read_from_str, ls_str_funcs)
        f_not = df.DiscreteFunction.read_from_str('f_3_2_19458')
        new_f = df.DiscreteFunction(range(3), {}, 3)
        f = df.commuting_functions_from_negative(new_f, premise, f_not).next()
        assert all(df.commute(f, f_other) for f_other in premise)
        assert df.commute(f, f_not) != True
        #Found: f_3_3_5170640158341
        #Time taken:133.394649029
        
    def test_prover_holds_identity(self):
        f_not = df.DiscreteFunction.read_from_str('f_3_1_21')
        premise = []
        new_f = df.DiscreteFunction(range(3), {}, 3)
        assert_raises(StopIteration, next,
                      df.commuting_functions_from_negative(new_f, premise, f_not))
        