'''
Akond Rahman 
May 22 2019 
Oracle Dataset Construction 
'''
import pandas as pd 
import numpy as np 

def mapDiffsToCateg(diff_, diff_categ, categ_dict):
    ful_list = [] 
    diff_IDs = diff_['DiffID'].tolist() 
    for diffID in diff_IDs:
        final_categ_val = 'None'        
        specific_df     = diff_[diff_['DiffID']==diffID]
        diff_hash_val   = specific_df['DiffHash'].tolist()[0]
        diff_repo_val   = specific_df['Repo'].tolist()[0]
        sub_categ_df    = diff_categ[diff_categ['DIFFID']==diffID]
        # print sub_categ_df.head() 
        r_, c_  = sub_categ_df.shape 
        if r_ > 0 :
            diff_cate_val   = sub_categ_df['CATEGID'].tolist()[0]
            if diff_cate_val in categ_dict:
                final_categ_val = categ_dict[diff_cate_val]

        ful_list.append((diffID, diff_hash_val, diff_repo_val, final_categ_val))
    final_df = pd.DataFrame(ful_list)
    return final_df


def findMismatches(oracle, tool):
    mismatch_list = []
    hashes = oracle['DIFF_HASH'].tolist() 
    for hash_ in hashes:
        categ_oracle = oracle[oracle['DIFF_HASH']==hash_]['CATEG'].tolist()[0]
        categ_tool   = tool[tool['HASH']==hash_]['CATEG'].tolist()[0]
        categ_repo   = tool[tool['HASH']==hash_]['REPO'].tolist()[0] 
        mismatch_list.append( (hash_, categ_oracle, categ_tool, categ_repo) ) 
    mismatch_df = pd.DataFrame(mismatch_list)
    return mismatch_df

if __name__=='__main__':
    diff_file  = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/closed-coding-2019/categ_diff2019.csv'
    diff_df    = pd.read_csv(diff_file)    
    # print diff_df.head()
    
    sub_file   = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/closed-coding-2019/categ_submission2019.csv'
    sub_df     = pd.read_csv(sub_file)
    diff_categ_df = sub_df.drop(['ID', 'STUDENTID', 'COUNT', 'EXTRA'], axis=1)
    # print diff_categ_df.head()

    categ_file = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/closed-coding-2019/category2019.csv'
    categ_df   = pd.read_csv(categ_file) 
    categ_map_df = categ_df.drop(['MESSAGE'], axis=1)
    categ_dict = categ_df.to_dict()['CATEG']
    # print categ_dict

    # full_df = mapDiffsToCateg(diff_df, diff_categ_df, categ_dict)
    # full_df.to_csv('/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/closed-coding-2019/FINAL_CATEG_MAPPING.csv')

    oracle_file = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/closed-coding-2019/LOCKED_FOR_PAPER_FINAL_CLASSI_OUTPUT_ORACLE.csv'
    oracle_df   = pd.read_csv(oracle_file)
    tool_file   = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/closed-coding-2019/ORACLE_CATEG_OUTPUT_SEMIFINAL.csv'
    tool_df     = pd.read_csv(tool_file)

    # mismatch_df = findMismatches(oracle_df, tool_df) 
    # mismatch_df.to_csv('/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/closed-coding-2019/FINAL_OUTPUT_ORACLE.csv')

    final_df = pd.merge(oracle_df, tool_df, on='HASH', how='inner')
    # final_df = final_df.drop_duplicates(['HASH'])
    final_df.to_csv('/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/closed-coding-2019/FINAL_CLASSI_OUTPUT_ORACLE.csv')