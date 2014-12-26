'''
Use with Nosetests (https://nose.readthedocs.org/en/latest/)

Created on Jun 9, 2014

@author: artreven
'''
import p_clones.express as ex
import p_clones.discrete_function as df

class Test:

    def setUp(self):
        self.dict_disj = {(0,0): 0, (0,1): 1,
                          (1,0): 1, (1,1): 1}
        self.df_disj = df.DiscreteFunction(domain=range(2), dict_f=self.dict_disj)
        self.dict_neg = {(0,): 1, (1,): 0}
        self.df_neg = df.DiscreteFunction(domain=range(2), dict_f=self.dict_neg)
        self.dict_imp = {(0,0): 1, (0,1): 1,
                         (1,0): 0, (1,1): 1}
        self.df_imp = df.DiscreteFunction(domain=range(2), dict_f=self.dict_imp)
        self.dict_conj = {(0,0): 0, (0,1): 0,
                          (1,0): 0, (1,1): 1}
        self.df_conj = df.DiscreteFunction(domain=range(2), dict_f=self.dict_conj)
        self.dict_id = {(0,): 0, (1,): 1}
        self.df_id = df.DiscreteFunction(domain=range(2), dict_f=self.dict_id)

    def tearDown(self):
        pass


    def test_p_express_disjneg_imp_2(self):
        print ex.p_express([self.df_disj, self.df_neg], self.df_imp)
        assert ex.p_express([self.df_disj, self.df_neg], self.df_imp)
        
    def test_p_express_imp_conj_2(self):
        print ex.p_express([self.df_imp,], self.df_conj)
        assert ex.p_express([self.df_imp,], self.df_conj)
        
    def test_p_express_1(self):
        f = df.DiscreteFunction.read_from_str('f_3_2_14001')
        F = map(df.DiscreteFunction.read_from_str, ['f_3_3_7612633065141',])
        assert ex.p_express(F, f)
        
    def test_p_express_2(self):
        f = df.DiscreteFunction.read_from_str('f_3_2_19458')
        F = map(df.DiscreteFunction.read_from_str, ['f_3_1_0', 'f_3_2_112',
                                                    'f_3_1_4', 'f_3_1_13',
                                                    'f_3_1_21', 'f_3_1_26',
                                                    'f_3_1_18'])
        assert ex.p_express(F, f)

    def test_p_express_not_1(self):
        f = df.DiscreteFunction.read_from_str('f_3_2_19601')
        F = map(df.DiscreteFunction.read_from_str, ['f_3_2_17222', 'f_3_1_26',
                                                    'f_3_1_21', 'f_3_1_23',
                                                    'f_3_1_13'])
        assert ex.p_express(F, f) == None
        
###############################################################################
        
    def test_equal(self):
        id_disj_conj = ex.equal(self.df_disj, self.df_conj)
        bool_4cube = [(0,0,0,0), (0,0,0,1),
                      (0,0,1,0), (0,0,1,1),
                      (0,1,0,0), (0,1,0,1),
                      (0,1,1,0), (0,1,1,1),
                      (1,0,0,0), (1,0,0,1),
                      (1,0,1,0), (1,0,1,1),
                      (1,1,0,0), (1,1,0,1),
                      (1,1,1,0), (1,1,1,1)]
        assert map(id_disj_conj, bool_4cube) == [1,1,1,0,
                                                 0,0,0,1,
                                                 0,0,0,1,
                                                 0,0,0,1]
        
    def test_conjunction(self):
        id_id_neg = ex.equal(self.df_id, self.df_neg)
        id_conj_neg = ex.equal(self.df_conj, self.df_neg)
        cl_id_neg__conj_neg = ex.conjunction(id_id_neg, id_conj_neg)
        input_ = [(0,0,0,1,1), (0,0,1,1,0),
                  (0,1,1,0,0), (1,1,0,0,0),
                  (1,1,1,0,0), (1,1,0,0,1),
                  (1,0,0,1,1), (1,0,1,1,0)]
        assert map(cl_id_neg__conj_neg, input_) == [0, 0, 0, 0,
                                                    0, 0, 1, 1]
        
    def test_identify_args(self):
        id_id_neg = ex.equal(self.df_id, self.df_neg)
        id_conj_neg = ex.equal(self.df_conj, self.df_neg)
        cl_id_neg__conj_neg = ex.conjunction(id_id_neg, id_conj_neg)
        cl3 = ex.permute_args(cl_id_neg__conj_neg, (2,1,3,2,2))
        input_ = [(0,0,0), (0,0,1),
                  (0,1,0), (0,1,1),
                  (1,0,0), (1,0,1),
                  (1,1,0), (1,1,1)]
        assert map(cl3, input_) == [0,0,1,0,0,0,0,0]
    
    def test_quantify(self):
        id_id_neg = ex.equal(self.df_id, self.df_neg)
        id_conj_neg = ex.equal(self.df_conj, self.df_neg)
        cl_id_neg__conj_neg = ex.conjunction(id_id_neg, id_conj_neg)
        cl3 = ex.permute_args(cl_id_neg__conj_neg, (2,1,3,2,2))
        cl2 = ex.quantify(cl3, 2)
        input_ = [(0,0), (0,1),
                  (1,0), (1,1)]
        assert map(cl2, input_) == [1,0,0,0]