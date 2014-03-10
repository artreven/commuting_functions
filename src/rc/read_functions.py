'''
Created on Feb 26, 2014

@author: artreven
'''
from copy import deepcopy

import fca.readwrite

import re
import rc.discrete_function
df = rc.discrete_function

path = '/home/artreven/Dropbox/personal/Scripts/AptanaWorkspace/relational_clones/comm_funcs/fdanilchenko_values.csv'
path_my_cxt = '/home/artreven/Dropbox/personal/Scripts/AptanaWorkspace/relational_clones/my_cxt.cxt'
path_cxt_dan = '/home/artreven/Dropbox/personal/Scripts/AptanaWorkspace/relational_clones/cxt_dan.cxt'

def read_dfuncs(path):
    domain = range(3)
    ls_funcs = []
    with open(path, 'r') as file_functions:
        for str_func in file_functions:
            values = re.findall(r'\d+', str_func)
            arity = 0
            while 'f(' == str_func[:2]:
                str_func = str_func[2:]
                arity +=1
            values = [int(x) - 1 for x in values]
            dict_func = dict(zip(df._get_total_domain(domain, arity), values))
            func = df.DiscreteFunction(domain, dict_func, arity)
            ls_funcs.append(func)
    return ls_funcs

def check():
    new_objs = list(set(cxt_dan.objects) - set(my_cxt.objects))
#     new_objs.pop()
#     new_objs.pop()
#     new_objs.pop()
#     new_objs.pop()
    new_obj = new_objs.pop()
    new_func = df.DiscreteFunction.read_from_str(new_obj)
    old_funcs = map(df.DiscreteFunction.read_from_str, my_cxt.objects)
    new_col = [df.commute(new_func, old_func)==True for old_func in old_funcs]
    
    #my_cxt.add_attribute(new_col, new_obj)
    new_row = new_col + [new_func.self_commuting(),]
    #my_cxt.add_object(new_row, new_obj)
    #intents = set(map(lambda x: frozenset(x.intent), my_cxt.concepts))
    new_intent = {str(old_func) for old_func in old_funcs
                  if df.commute(new_func, old_func)==True}
    imp_basis = my_cxt.get_aibasis()
    for imp in imp_basis:
        if imp.premise <= new_intent:
            if not (imp.conclusion <= new_intent):
                print new_obj
                print new_intent
                print imp
                conc = map(df.DiscreteFunction.read_from_str, (imp.conclusion - new_intent))
                print conc
                break
    ls_premise = map(df.DiscreteFunction.read_from_str, imp.premise)
    print new_func.output_dict()
    print new_func
    t_limit = None
    for f_not in conc:
        print
        print 'Premise: ', map(str, ls_premise)
        print 'Conclusion: ', f_not
        print 'Time limit: ', t_limit
        new_f = df.DiscreteFunction(range(3), {}, 3)
        #return df.commuting_functions_batch(new_f, ls_premise, [f_not,], wait=t_limit)
        f = df.commuting_functions_batch(new_f, ls_premise, [f_not,], wait=t_limit).next()
        print [df.commute(f, f_other) for f_other in ls_premise]
        print df.commute(f, f_not)
        
def check2():
    f_3_1_14 = df.DiscreteFunction.read_from_str('f_3_1_14')
    f_3_1_0 = df.DiscreteFunction.read_from_str('f_3_1_0')
    f_3_1_13 = df.DiscreteFunction.read_from_str('f_3_1_13') 
    f_3_1_26 = df.DiscreteFunction.read_from_str('f_3_1_26')
    f_3_1_21 = df.DiscreteFunction.read_from_str('f_3_1_21')
    f_3_2_10609 = df.DiscreteFunction.read_from_str('f_3_2_10609')
    ls_premise = [f_3_1_14, f_3_1_0, f_3_1_13, f_3_1_21, f_3_1_26, f_3_2_10609]
    
    f_3_2_19681 = df.DiscreteFunction.read_from_str('f_3_2_19681')
    f_not = f_3_2_19681
    new_f = df.DiscreteFunction(range(3), dict(), 3)
    f = df.commuting_functions_batch(new_f, ls_premise, [f_not,]).next()
    print all(df.commute(f, f_other) for f_other in ls_premise)
    print df.commute(f, f_not)
    return f

def check3():
    f_3_3_7582141826698 = df.DiscreteFunction.read_from_str('f_3_3_7582141826698')
    f_3_1_22 = df.DiscreteFunction.read_from_str('f_3_1_22')
    ls_premise = [f_3_3_7582141826698,]
    f_not = f_3_1_22
    new_f = df.DiscreteFunction(range(3), dict(), 3)
    try:
        f = df.commuting_functions_batch(new_f, ls_premise, [f_not,]).next()
        print all(df.commute(f, f_other) for f_other in ls_premise)
        print df.commute(f, f_not)
    except StopIteration:
        return None

if __name__ == '__main__':
    import cProfile
    import copy
    my_cxt = fca.readwrite.read_cxt(path_my_cxt)
    cxt_dan = fca.readwrite.read_cxt(path_cxt_dan)
#     old_objs = my_cxt.objects
#     old_funcs = map(df.DiscreteFunction.read_from_str, old_objs)
#     ls_funcs = ["f_3_2_3271", "f_3_2_12979", "f_3_2_6417", "f_3_2_19595", "f_3_2_3936", "f_3_2_15634", "f_3_2_11503", "f_3_2_18063", "f_3_3_7562641645683", "f_3_2_7381", "f_3_2_17820", "f_3_2_15465", "f_3_3_3812411301552", "f_3_3_6641160425573", "f_3_3_7581754385757", "f_3_2_15951", "f_3_3_7593391169757", "f_3_2_13346", "f_3_1_7", "f_3_2_9073", "f_3_2_13009", "f_3_3_7593439949091", "f_3_2_16402", "f_3_2_1506", "f_3_2_14001", "f_3_2_19569", "f_3_2_19317", "f_3_2_13203", "f_3_2_19650", "f_3_2_19622", "f_3_2_9842", "f_3_2_19676", "f_3_2_19680", "f_3_2_17220", "f_3_2_4455", "f_3_2_162", "f_3_2_15716", "f_3_2_8748", "f_3_2_19652", "f_3_3_7625403765657", "f_3_2_15663", "f_3_3_7625403771462", "f_3_3_7625389238847", "f_3_2_17222", "f_3_2_17131", "f_3_2_768", "f_3_2_19601", "f_3_2_10570", "f_3_2_16401", "f_3_2_15411", "f_3_2_18603", "f_3_3_7538621575365", "f_3_2_15393", "f_3_1_12", "f_3_2_19326", "f_3_2_19314", "f_3_1_23", "f_3_2_19570", "f_3_2_17139", "f_3_2_19679", "f_3_2_19521", "f_3_3_6088151958012", "f_3_2_18589", "f_3_2_17361", "f_3_1_2", "f_3_3_7625403765063", "f_3_2_17337", "f_3_2_18913", "f_3_2_18576", "f_3_1_14", "f_3_2_19520", "f_3_3_5115162730851", "f_3_2_2268", "f_3_3_7625594689806", "f_3_3_7580592121860", "f_3_2_5082", "f_3_2_15633", "f_3_2_4860", "f_3_3_7570117242603", "f_3_3_7593391528911", "f_3_3_7593377002614", "f_3_2_19325", "f_3_2_2460", "f_3_2_10609", "f_3_3_7538687762733", "f_3_2_19309", "f_3_2_6336", "f_3_2_17414", "f_3_2_13122", "f_3_3_6998283997146", "f_3_3_7623079246341", "f_3_3_7625341409157", "f_3_2_112", "f_3_3_7612633065141", "f_3_3_7625016344412", "f_3_2_19514", "f_3_2_6561", "f_3_3_7625403783045", "f_3_2_9840", "f_3_2_10578", "f_3_2_4941", "f_3_2_81", "f_3_3_7538686168410", "f_3_2_2187", "f_3_3_7625389418181", "f_3_2_9729", "f_3_2_3168", "f_3_2_16393", "f_3_3_31431074193", "f_3_2_17409", "f_3_3_7582141826698", "f_3_2_19539", "f_3_3_7613781150231", "f_3_1_25", "f_3_2_17141", "f_3_2_15664", "f_3_2_9837", "f_3_3_7625409079311", "f_3_1_24", "f_3_2_19629", "f_3_3_7625595260664", "f_3_2_2541", "f_3_2_18065", "f_3_1_19", "f_3_1_0", "f_3_1_17", "f_3_1_5", "f_3_1_15", "f_3_1_3", "f_3_2_16514", "f_3_2_19677", "f_3_2_19197", "f_3_2_14600", "f_3_2_10610", "f_3_3_6354277129881", "f_3_2_19674", "f_3_1_1", "f_3_2_3280", "f_3_3_7624822603104", "f_3_2_18146", "f_3_1_4", "f_3_2_18222", "f_3_3_7520843358027", "f_3_1_6", "f_3_1_20", "f_3_2_19566", "f_3_2_19575", "f_3_2_12301", "f_3_2_15552", "f_3_1_10", "f_3_3_7625418645249", "f_3_2_15746", "f_3_1_16", "f_3_2_19541", "f_3_2_19071", "f_3_2_9832", "f_3_2_14762", "f_3_2_15309", "f_3_3_7602158535561", "f_3_2_19062", "f_3_2_4536", "f_3_2_4920", "f_3_2_108", "f_3_2_2430", "f_3_3_6069135664605", "f_3_1_8", "f_3_2_19599", "f_3_2_18144", "f_3_2_19681", "f_3_2_15660", "f_3_2_1536", "f_3_2_19458", "f_3_3_7614957760605", "f_3_2_13008", "f_3_2_6366", "f_3_2_15582", "f_3_2_10571", "f_3_2_18914", "f_3_1_22", "f_3_1_18", "f_3_2_19598", "f_3_2_14967", "f_3_1_13", "f_3_2_15921", "f_3_2_14580", "f_3_2_9111", "f_3_2_10569", "f_3_2_4374", "f_3_3_7582012670133", "f_3_1_9", "f_3_3_6640193477037", "f_3_2_12241", "f_3_2_10557", "f_3_2_10579", "f_3_2_19678", "f_3_3_7582141826685", "f_3_2_17496", "f_3_2_9103", "f_3_2_4725", "f_3_1_26", "f_3_2_19035", "f_3_2_17121", "f_3_2_19332", "f_3_2_9072", "f_3_3_7625260079001", "f_3_2_15776", "f_3_2_16389", "f_3_2_6673", "f_3_1_21"]
#     new_objs = list(set(cxt_dan.objects) - set(ls_funcs))
#     new_objs_old = list(set(cxt_dan.objects) - set(my_cxt.objects))
    print check2()
    print check3()