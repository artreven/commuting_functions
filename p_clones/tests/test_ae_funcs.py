'''
Use with Nosetests (https://nose.readthedocs.org/en/latest/)

Created on Dec 24, 2014

@author: artreven
'''
import os
import shutil

import fca
import auto_ae.ae as ae

import p_clones.discrete_function as df
import p_clones.main as main

def test_ce_finder():
    premise = {'f_3_3_7625409079311', 'f_3_3_7613781150231', 'f_3_3_7030487768325', 'f_3_2_17361', 'f_3_2_19575', 'f_3_2_19332', 'f_3_1_2', 'f_3_3_7614957760605', 'f_3_3_6088926820179', 'f_3_1_24', 'f_3_2_19629', 'f_3_1_21', 'f_3_3_7625418645249'}
    premise = map(repr, map(df.DiscreteFunction.str2df, premise))
    conclusion = {repr(df.DiscreteFunction.str2df('f_3_3_7593439949091'))}
    imp = fca.Implication(premise, conclusion)
    ce, reason = main.ce_finder(imp, wait=float('inf'))
    assert ce
    
def test_go_on():
    test_file_path = './test_find_oae.txt'
    funcs = ['f_2_1_0', 'f_2_1_1', 'f_2_1_2', 'f_2_3_232']
    cxt = main.init_cxt(funcs)
    new_funcs = main.find_oa_extension(cxt, test_file_path,
                                       wait=float('inf'))
    assert new_funcs
    ### Clean up if assertion holds
    os.remove(test_file_path)
    
def test_ae_2():
    test_dir = './test_run'
    funcs = ['f_2_1_0']
    cxt = main.init_cxt(funcs)
    ae_cfs = ae.AE(test_dir, cxt, main.has_attribute, main.ce_finder,
                   main.go_on, attributes_growing=True)
    ae_cfs.run(10)
    assert len(ae_cfs.cxt) == 7
    ### Clean up if assertion holds
    shutil.rmtree(test_dir)