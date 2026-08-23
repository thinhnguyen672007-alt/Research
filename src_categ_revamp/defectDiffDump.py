'''
Akond Rahman 
Fed 27, 2019 
Get diffs for defect-related commits 
'''
import pandas as pd 
import numpy as np 
import csv 
import os 
import subprocess

def getDiffStr(repo_path_p, commit_hash_p, file_p):
   
   cdCommand   = "cd " + repo_path_p + " ; "
   theFile     = os.path.relpath(file_p, repo_path_p)
   
   diffCommand = " git diff  " + commit_hash_p + " " + theFile + "  "
   command2Run = cdCommand + diffCommand
   diff_output = subprocess.check_output(['bash','-c', command2Run])

   return diff_output



def dumpDefectDiffText(df_p, fil_p):
    dump_str = ''
    cnt  = 0 
    commit_hash_list = np.unique( df_p['COMMIT'].tolist() )
    for commit_hash in commit_hash_list:
        commit_df        = df_p[df_p['COMMIT']==commit_hash]
        commit_pp_files  = commit_df['FILE'].tolist()
        commit_repo_path = commit_df['REPO'].tolist()[0]
        text_comm        = commit_df['MESSAGE'].tolist()[0]
        date_time        = commit_df['TIME'].tolist()[0]
        for file_ in commit_pp_files: 
            diff_content_str = getDiffStr(commit_repo_path, commit_hash, file_)
            if(len(diff_content_str) > 0 ):
                cnt += 1 
                print '='*25 + ':'*3  + commit_repo_path  + ':'*3 + commit_hash + ':'*3 + 'START!' + '='*25
                print file_ 
                print '*'*10
                print diff_content_str
                print '*'*10
                print text_comm
                print '*'*10
                print 'DECISION===>:'
                print '*'*10
                print '='*25 + ':'*3 + str(cnt) + ':'*3  + date_time + ':'*3 + 'END!!!' + '='*25    

def dumpContentIntoFile(strP, fileP):
  fileToWrite = open( fileP, 'w')
  fileToWrite.write(strP )
  fileToWrite.close()
  return str(os.stat(fileP).st_size)

def dumpDefectCommitText(df_p, fil_p):
    dump_str = ''
    cnt  = 0 
    commit_hash_list = np.unique( df_p['COMMIT'].tolist() )
    for commit_hash in commit_hash_list:
        commit_df        = df_p[df_p['COMMIT']==commit_hash]
        commit_pp_files  = commit_df['FILE'].tolist()
        commit_repo_path = commit_df['REPO'].tolist()[0]
        text_comm        = commit_df['MESSAGE'].tolist()[0]
        date_time        = commit_df['TIME'].tolist()[0]
        
        dump_str = dump_str + date_time + ','  + commit_repo_path + ',' + commit_hash + ',' + text_comm + ',' + '\n' 

    dumpContentIntoFile(dump_str, fil_p) 


if __name__=='__main__':
   defect_categ_file      = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/OSTK_PUPP_COMM_ONLY_DEFE.csv'
   categ_defect_dump_file = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/OSTK_PUPP_ONLY_DEFE_DUMP.txt'
   defect_categ_df   = pd.read_csv(defect_categ_file)
   #dumpDefectDiffText(defect_categ_df, categ_defect_dump_file) 

   commit_defect_dump_file = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/OSTK_PUPP_ONLY_DEFE_COMM.csv'
   #dumpDefectCommitText(defect_categ_df, commit_defect_dump_file) 