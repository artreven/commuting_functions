'''
Use with Nosetests (https://nose.readthedocs.org/en/latest/)

Created on Mar 20, 2014

@author: artreven
'''
from nose.tools import assert_raises, nottest  # @UnresolvedImport

import rc.discrete_function
df = rc.discrete_function

class Test():
    def setUp(self):
        self.f1 = df.DiscreteFunction(range(3), dict(), 1)
        self.f2 = df.DiscreteFunction(range(3), dict(), 2)
        self.f3 = df.DiscreteFunction(range(3), dict(), 3)

    def tearDown(self):
        pass
    
    def test_from_negative_raises1(self):
        f_other = df.DiscreteFunction.read_from_str('f_3_2_19681')
        f_not = df.DiscreteFunction.read_from_str('f_3_1_25')
        assert_raises(StopIteration, next, 
                      df.commuting_functions_from_negative(self.f3,
                                                           [f_other,],
                                                           f_not,
                                                           wait=10))
        
    def test_from_negative_raises2(self):
        f_other = df.DiscreteFunction.read_from_str('f_3_3_7612633065141')
        f_not = df.DiscreteFunction.read_from_str('f_3_2_14001')
        assert_raises(StopIteration, next, 
                      df.commuting_functions_from_negative(self.f3,
                                                           [f_other,],
                                                           f_not,
                                                           wait=10))
        
    def test_from_negative_raises3(self):
        f_other = df.DiscreteFunction.read_from_str('f_3_1_25')
        f_not = df.DiscreteFunction.read_from_str('f_3_1_26')
        assert_raises(StopIteration, next, 
                      df.commuting_functions_from_negative(self.f3,
                                                           [f_other,],
                                                           f_not,
                                                           wait=10))
        
    
    def test_from_negative_raises4(self):
        # takes nearly 35 secs
        f_other = df.DiscreteFunction.read_from_str('f_3_3_7625389238847')
        f_not = df.DiscreteFunction.read_from_str('f_3_3_7625389418181')
        assert_raises(StopIteration, next, 
                      df.commuting_functions_from_negative(self.f3,
                                                           [f_other,],
                                                           f_not))
        
    def test_from_negative_raises5(self):
        f_other = df.DiscreteFunction.read_from_str('f_3_2_6561')
        f_not = df.DiscreteFunction.read_from_str('f_3_1_9')
        assert_raises(StopIteration, next, 
                      df.commuting_functions_from_negative(self.f3,
                                                           [f_other,],
                                                           f_not,
                                                           wait=10))
        
    def test_from_negative_raises6(self):
        # took 23 secs with batch
        ls_f_other = map(df.DiscreteFunction.read_from_str,
                         ['f_3_1_3', 'f_3_1_21', 'f_3_3_7570117242603'])
        f_not = df.DiscreteFunction.read_from_str('f_3_3_7538621575365')
        assert_raises(StopIteration, next,
                      df.commuting_functions_from_negative(self.f3,
                                                           ls_f_other,
                                                           f_not))
        
    def test_from_negative_finds1(self):
        ls_f_other = map(df.DiscreteFunction.read_from_str,
                         ['f_3_1_14', 'f_3_1_0', 'f_3_1_13',
                          'f_3_1_26', 'f_3_1_21', 'f_3_2_10609'])
        f_not = df.DiscreteFunction.read_from_str('f_3_2_19681')
        f = next(df.commuting_functions_from_negative(self.f3,
                                                      ls_f_other,
                                                      f_not))
        assert all(df.commute(f, f_other) == True for f_other in ls_f_other)
        assert not df.commute(f, f_not) == True
        
    def test_from_negative_finds2(self):
        # before it took nearly 8 secs, answer was f_3_3_7030489362648
        ls_f_other = map(df.DiscreteFunction.read_from_str,
                         ['f_3_3_7625409079311', 'f_3_3_7613781150231',
                          'f_3_3_7030487768325', 'f_3_2_17361', 'f_3_2_19575',
                          'f_3_2_19332', 'f_3_1_2', 'f_3_3_7614957760605',
                          'f_3_3_6088926820179', 'f_3_1_24',
                          'f_3_2_19629', 'f_3_1_21', 'f_3_3_7625418645249'])
        f_not = df.DiscreteFunction.read_from_str('f_3_3_7593439949091')
        f = next(df.commuting_functions_from_negative(self.f3,
                                                      ls_f_other,
                                                      f_not))
        assert all(df.commute(f, f_other) == True for f_other in ls_f_other)
        assert not df.commute(f, f_not) == True
        
    def test_from_negative_finds3(self):
        # before it took nearly 143 secs, answer was f_3_3_6099789120879
        ls_f_other = map(df.DiscreteFunction.read_from_str,
                         ['f_3_2_17222', 'f_3_1_26', 'f_3_1_21', 'f_3_1_23', 'f_3_1_13'])
        f_not = df.DiscreteFunction.read_from_str('f_3_2_19601')
        f = next(df.commuting_functions_from_negative(self.f3,
                                                      ls_f_other,
                                                      f_not))
        assert all(df.commute(f, f_other) == True for f_other in ls_f_other)
        assert not df.commute(f, f_not) == True