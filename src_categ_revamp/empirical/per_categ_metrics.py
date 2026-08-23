'''
Akond Rahman 
June 27, 2019 
Get Metrics Per Category 
'''
import pandas as pd 
import numpy as np 

metric_list = ['MOD_FILES', 'DIRS',	'TOT_SLOC',	'SPREAD', 'DEV_CNT_MOD_FILES', 'DEV_EXP', 'DEV_REXP']

def changeCategIfNeeded(categ_param):
    categ_mod = ''
    mod_dict  = {
                'BUILD_DEFECT':'SERVICE_DEFECT', 
                'DB_DEFECT':'SERVICE_DEFECT', 
                'INSTALL_DEFECT':'SERVICE_DEFECT', 
                'LOG_DEFECT':'SERVICE_DEFECT', 
                'NET_DEFECT':'SERVICE_DEFECT', 
                'RACE_DEFECT':'SERVICE_DEFECT'
                }
    if categ_param in mod_dict:
        categ_mod = mod_dict[categ_param]
    else:
        categ_mod = categ_param
    return categ_mod

def getMetricDist(categ_f, metric_f): 
    categ_df  = pd.read_csv(categ_f) 
    metric_df = pd.read_csv(metric_f) 
    result_df = pd.merge(categ_df, metric_df, on=['HASH'])
    result_df['CHANGED_CATEG'] = result_df['CATEG'].apply(changeCategIfNeeded) 
    categ_list = np.unique(result_df['CHANGED_CATEG'].tolist())
    for categ_ in categ_list:
        per_categ_df = result_df[result_df['CHANGED_CATEG']==categ_]
        print 'CATEGORY:',  categ_
        for metr_ in metric_list:
            metr_vals = per_categ_df[metr_].tolist() 
            if len(metr_vals) > 0 :
                print 'METRIC:{}, MIN:{}, MEDIAN:{}, AVG:{}, MAX:{}'.format(metr_,  min(metr_vals), np.median(metr_vals), np.mean(metr_vals), max(metr_vals) )
                print '-'*10
            else: 
                print 'METRIC:{}, MIN:{}, MEDIAN:{}, AVG:{}, MAX:{}'.format(metr_, 0, 0, 0, 0 )
                print '-'*10                
        print '*'*50

def getFileDist(categ_f, hash_mapping_f): 
    categ_df = pd.read_csv(categ_f) 
    map_df   = pd.read_csv(hash_mapping_f) 
    full_df  = pd.merge(categ_df, map_df, on=['HASH'])    
    # print full_df.tail() 
    all_files = list(np.unique(full_df['FILE'].tolist())) 
    print 'Dataset name:', categ_f.split('/')[-1] 
    print 'Total count of Puppet scripts:', len(all_files)
    print '='*50 
    atleat_one_files = []
    full_df['CHANGED_CATEG'] = full_df['CATEG'].apply(changeCategIfNeeded) 
    categ_list = np.unique(full_df['CHANGED_CATEG'].tolist())
    for categ_ in categ_list:
        per_categ_file_list = [] 
        for file_ in all_files:
            file_df = full_df[full_df['FILE']==file_]
            categ_file_df = file_df[file_df['CATEG']==categ_]
            files_categ   = list( np.unique(categ_file_df['FILE'].tolist() ) ) 
            per_categ_file_list = per_categ_file_list + files_categ
            if categ_!= 'NO_DEFECT': 
                atleat_one_files = atleat_one_files + files_categ 
        per_categ_file_prop = round(float(len(per_categ_file_list)) / float(len(all_files)), 5)* 100
        if categ_!= 'NO_DEFECT': 
            print 'CATEGORY:{}, SCRIPT_PROP(%):{}'.format(categ_, per_categ_file_prop) 
            print '*'*25
    atleast_one = round( (float( len( np.unique( atleat_one_files ) ) )    / float(len(all_files)) ) , 5)* 100
    print 'Puppet scripts with at least one defect category(%):', atleast_one 
    print '='*50     

def analyzeCommitsForCoOccurence(file_name):
    dict_output          = {2:[], 3: [], 4: [], 5: [], 6: [], 7:[], 8:[]}
    categ_df_full        = pd.read_csv(file_name) 
    df_only_defect_categ = categ_df_full[categ_df_full['CATEG']!='NO_DEFECT']
    df_only_defect_categ['CHANGED_CATEG'] = df_only_defect_categ['CATEG'].apply(changeCategIfNeeded) 
    commits              = np.unique( df_only_defect_categ['HASH'].tolist() )
    for commit_hash in commits:
        commit_df        = df_only_defect_categ[df_only_defect_categ['HASH']==commit_hash]
        commit_categs    = list ( np.unique( commit_df['CHANGED_CATEG'].tolist() ) )
        commit_categ_cnt = len(commit_categs)  
        if commit_categ_cnt > 1:
            dict_output[commit_categ_cnt] = dict_output[commit_categ_cnt] + [commit_hash]  
    return dict_output     

def getCommitCoOccurence(categ_file): 
    print categ_file 
    categ_df_full        = pd.read_csv(categ_file) 
    categ_commits        = list( np.unique( categ_df_full['HASH'].tolist() ) )
    dict_output = analyzeCommitsForCoOccurence(categ_file)
    print '*'*50
    for k_, v_ in dict_output.iteritems():
        def_pop = round( (float(len(v_))/float(len(categ_commits)) ) * 100, 5)
        print '{} categories of defects observed for {}% commits (defect proportion)'.format(k_, def_pop)
    print '*'*50
    return dict_output

def getFileCoOccurence(categ_file, hash_script_file): 
    print categ_file 
    hash_script_df_full        = pd.read_csv(hash_script_file)  
    all_scripts = np.unique(hash_script_df_full['FILE'].tolist())
    dict_output = analyzeCommitsForCoOccurence(categ_file)
    print '*'*50
    for k_, v_ in dict_output.iteritems():
        script_list = [] 
        for hash_ in v_:
            hash_df      = hash_script_df_full[hash_script_df_full['HASH']==hash_]
            hash_scripts = list( np.unique( hash_df['FILE'].tolist() ) )
            script_list  = script_list + hash_scripts
        script_list =  list( np.unique( script_list ) )
        fil_pop = round( (float(len(script_list))/float(len(all_scripts)) ) * 100, 5)
        print '{} categories of defects observed for {}% scripts (script proportion)'.format(k_, fil_pop)
    print '*'*50
    return dict_output


if __name__=='__main__': 
    # categ_output_file  = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/GHUB_CATEG_OUTPUT_FINAL.csv'
    # metric_output_file = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/GHUB_METRICS_OUTPUT_FINAL.csv' 
    # hash_mapping_file  = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/GHUB_HASH_FILE_OUTPUT_FINAL.csv'

    # categ_output_file  = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/MOZI_CATEG_OUTPUT_FINAL.csv'
    # metric_output_file = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/MOZI_METRICS_OUTPUT_FINAL.csv' 
    # hash_mapping_file  = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/MOZI_HASH_FILE_OUTPUT_FINAL.csv'

    # categ_output_file  = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/OSTK_CATEG_OUTPUT_FINAL.csv'
    # metric_output_file = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/OSTK_METRICS_OUTPUT_FINAL.csv' 
    # hash_mapping_file  = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/OSTK_HASH_FILE_OUTPUT_FINAL.csv' 

    # categ_output_file  = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/WIKI_CATEG_OUTPUT_FINAL.csv'
    # metric_output_file = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/WIKI_METRICS_OUTPUT_FINAL.csv' 
    # hash_mapping_file  = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/WIKI_HASH_FILE_OUTPUT_FINAL.csv' 

    '''
    Config sub category 
    '''
    # categ_output_file  = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/GHUB_CATEG_SUBCONFIG_FINAL.csv'
    # hash_mapping_file  = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/GHUB_HASH_FILE_OUTPUT_FINAL.csv'

    # categ_output_file  = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/MOZI_CATEG_SUBCONFIG_FINAL.csv'
    # hash_mapping_file  = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/MOZI_HASH_FILE_OUTPUT_FINAL.csv'

    # categ_output_file  = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/OSTK_CATEG_SUBCONFIG_FINAL.csv'
    # hash_mapping_file  = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/OSTK_HASH_FILE_OUTPUT_FINAL.csv' 

    # categ_output_file  = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/WIKI_CATEG_SUBCONFIG_FINAL.csv'
    # hash_mapping_file  = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/WIKI_HASH_FILE_OUTPUT_FINAL.csv'


    # RQ3 - Part#A, not used in paper
    # getMetricDist(categ_output_file, metric_output_file)
    # RQ3 - Part#B,  used in paper
    getFileDist(categ_output_file, hash_mapping_file) 

    # RQ3 - Part#C : Co-occurrence , not used in paper
    # getCommitCoOccurence(categ_output_file)
    # RQ3 - Part#D : Co-occurrence , not used in paper
    # getFileCoOccurence(categ_output_file, hash_mapping_file) 