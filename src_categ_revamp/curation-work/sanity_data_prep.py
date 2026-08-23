'''
Code to create sanity check dataset 
Akond Rahman
June 04, 2019 
'''
import pandas as pd 
import numpy as np 

if __name__=='__main__': 
    oracle_file = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/closed-coding-2019/LOCKED_ORACLE_DATASET.csv'
    oracle_df   = pd.read_csv(oracle_file)
    ost_file    = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/closed-coding-2019/ORACLE_CATEG_OUTPUT_SEMIFINAL.csv'
    ost_df      = pd.read_csv(ost_file)

    common_df      = oracle_df.merge(ost_df, on=['HASH'], how = 'inner')
    non_oracle_df  = ost_df[(~ ost_df.HASH.isin(common_df.HASH))]

    non_oracle_df.to_csv('/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/sanity-check-2019/OST_SANITY.csv', index=False) 
