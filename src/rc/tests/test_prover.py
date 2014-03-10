'''
Use with Nosetests (https://nose.readthedocs.org/en/latest/)

Created on Mar 2, 2014

@author: artreven
'''
import rc.discrete_function
import rc.prover
df = rc.discrete_function

class Test:

    def setUp(self):
        pass

    def tearDown(self):
        pass


    def test_prover1(self):
        f_other1 = df.DiscreteFunction.read_from_str('f_3_2_17496')
        f_other2 = df.DiscreteFunction.read_from_str('f_3_1_21')
        f_not = df.DiscreteFunction.read_from_str('f_3_1_18')
        premise = [f_other1, f_other2]
        conc = [f_not,]
        assert rc.prover.prover(premise, conc)
        
    def test_prover2(self):
        f_other1 = df.DiscreteFunction.read_from_str('f_3_2_17496')
        f_other2 = df.DiscreteFunction.read_from_str('f_3_1_21')
        f_not = df.DiscreteFunction.read_from_str('f_3_2_13122')
        premise = [f_other1, f_other2]
        conc = [f_not,]
        assert rc.prover.prover(premise, conc)
        
    def test_prover3(self):
        f_other1 = df.DiscreteFunction.read_from_str('f_3_1_8')
        f_other2 = df.DiscreteFunction.read_from_str('f_3_1_21')
        f_not = df.DiscreteFunction.read_from_str('f_3_1_18')
        premise = [f_other1, f_other2]
        conc = [f_not,]
        assert rc.prover.prover(premise, conc)
        
    def test_prover_holds_identity(self):
        f_not = df.DiscreteFunction.read_from_str('f_3_1_21')
        premise = []
        conc = [f_not,]
        assert rc.prover.prover(premise, conc) 