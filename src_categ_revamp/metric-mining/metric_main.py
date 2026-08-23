'''
Akond Rahman 
April 12, 2019 
Mining metrics: Main 
'''
import numpy as np 
import pandas as pd 
import cPickle as pickle
import metric_miner 
import os 
import csv 
import time
import datetime

def giveTimeStamp():
  tsObj = time.time()
  strToret = datetime.datetime.fromtimestamp(tsObj).strftime('%Y-%m-%d %H:%M:%S')
  return strToret

def getEligibleProjects(fileNameParam):
  repo_list = []
  with open(fileNameParam, 'rU') as f:
    reader = csv.reader(f)
    for row in reader:
      repo_list.append(row[0])
  return repo_list
'''
This script goes to each repo and mines commits and get metrics for each commit 
'''
###  columns=['COMMIT_HASH', 'FILE_CNT', 'DIR_CNT', 'LOC_MODI' 'SPREAD', 'DEVS_FILE', 'DEVS_EXP', 'DEVS_REXP']

if __name__=='__main__': 
  metric_flag = True  
  t1 = time.time()
  print 'Started at:', giveTimeStamp()
  print '*'*100  

  orgName='ghub-downloads'
  # out_csv_fil = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/GHUB_METRICS_OUTPUT_FINAL.csv'
  # out_hash_file = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/GHUB_HASH_FILE_OUTPUT_FINAL.csv'

  # orgName     = 'mozilla-releng-downloads'
  # out_csv_fil = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/MOZI_METRICS_OUTPUT_FINAL.csv'
  # out_hash_file = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/MOZI_HASH_FILE_OUTPUT_FINAL.csv'

  # orgName='openstack-downloads'
  # out_csv_fil = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/OSTK_METRICS_OUTPUT_FINAL.csv'
  # out_hash_file = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/OSTK_HASH_FILE_OUTPUT_FINAL.csv'  

  # orgName='wikimedia-downloads'
  # out_csv_fil = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/WIKI_METRICS_OUTPUT_FINAL.csv'
  # out_hash_file = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/WIKI_HASH_FILE_OUTPUT_FINAL.csv'  

  fileName          = '/Users/akond/ICSE2020_PUPP_REPOS/'  + orgName + '/' + 'eligible_repos.csv' 
  elgibleRepos      = getEligibleProjects(fileName)
  metrics_all_proj  = [] 
  if metric_flag: # this branch gets metrics 
    for proj_ in elgibleRepos:
      metrics_as_list   = metric_miner.runMiner(orgName, proj_, 'master')    
      metrics_all_proj = metrics_all_proj + metrics_as_list 

    final_metric_df = pd.DataFrame(metrics_all_proj)
    print final_metric_df.head() 
    final_metric_df.to_csv(out_csv_fil, header=['HASH', 'MOD_FILES', 'DIRS', 'TOT_SLOC', 'SPREAD', 'DEV_CNT_MOD_FILES', 'DEV_EXP', 'DEV_REXP'], index=False)   
  else:  # this branch gets file names and corresponding hashes 
    for proj_ in elgibleRepos:
      files_as_list     = metric_miner.getPuppFilesNHashes(orgName, proj_, 'master')    
      metrics_all_proj  = metrics_all_proj + files_as_list

    final_metric_df = pd.DataFrame(metrics_all_proj)
    print final_metric_df.head() 
    final_metric_df.to_csv(out_hash_file, header=['HASH', 'FILE'], index=False)     
  
  # '''
  # to get GitHub emails 
  # '''
  # all_emails = []
  # email_str = ''
  # email_file = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/GHUB_CATEG_OUTPUT_FINAL.csv'
  # email_df = pd.read_csv(email_file) 
  # all_ghub_hashes = email_df['HASH'].tolist() 
  # for hash_ in all_ghub_hashes:
  #   repo_         = email_df[email_df['HASH']==hash_]['REPO'].tolist()[0]
  #   author_emails = metric_miner.getAuthorOfHash(hash_, repo_) 
  #   all_emails    = all_emails + author_emails 

  # all_emails = list(np.unique(all_emails)) 
  # for email_ in all_emails:
  #   email_str = email_str + email_ + ',' + '\n'
  # print '*'*100
  # print email_str 
  # print '*'*100

  print '*'*100
  print 'Ended at:', giveTimeStamp()
  print '*'*100
  t2 = time.time()
  time_diff = round( (t2 - t1 ) / 60, 5) 
  print "Duration: {} minutes".format(time_diff)
  print '*'*100  