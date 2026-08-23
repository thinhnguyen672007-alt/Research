'''
Akond Rahman 
Dec 02, 2018 
Revamping Defect Categ project : Extraction 
'''
import os 
import csv 
import numpy as np
import sys
from git import Repo
import  subprocess
import time 
import  datetime 
import cPickle as pickle 
reload(sys)
sys.setdefaultencoding('utf8')

def getEligibleProjects(fileNameParam):
  repo_list = []
  with open(fileNameParam, 'rU') as f:
    reader = csv.reader(f)
    for row in reader:
      repo_list.append(row[0])
  return repo_list

def getPuppetFilesOfRepo(repo_dir_absolute_path):
    pp_, non_pp = [], []
    for root_, dirs, files_ in os.walk(repo_dir_absolute_path):
       for file_ in files_:
           full_p_file = os.path.join(root_, file_)
           if((os.path.exists(full_p_file)) and ('EXTRA_AST' not in full_p_file) ):
             if (full_p_file.endswith('.pp')):
               pp_.append(full_p_file)
    return pp_

def getChefFilesOfRepo(repo_dir_absolute_path):
    rb_  = [] 
    for root_, dirs, files_ in os.walk(repo_dir_absolute_path):
       for file_ in files_:
           full_p_file = os.path.join(root_, file_)
           if((os.path.exists(full_p_file)) and ('EXTRA_AST' not in full_p_file) ):
             if (('cookbooks' in full_p_file) and (full_p_file.endswith('.rb'))):
               rb_.append(full_p_file)
    return rb_

def getRelPathOfFiles(all_pp_param, repo_dir_absolute_path):
  common_path = repo_dir_absolute_path
  files_relative_paths = [os.path.relpath(path, common_path) for path in all_pp_param]
  return files_relative_paths 

def getPuppRelatedCommits(repo_dir_absolute_path, ppListinRepo, branchName='master'):
  mappedPuppetList=[]
  track_exec_cnt = 0
  repo_  = Repo(repo_dir_absolute_path)
  all_commits = list(repo_.iter_commits(branchName))
  for each_commit in all_commits:
    track_exec_cnt = track_exec_cnt + 1

    cmd_of_interrest1 = "cd  " + repo_dir_absolute_path + " ; "
    cmd_of_interrest2 = "git show --name-status " + str(each_commit)  +  "  | awk '/.pp/ {print $2}'"
    cmd_of_interrest = cmd_of_interrest1 + cmd_of_interrest2
    commit_of_interest  = subprocess.check_output(['bash','-c', cmd_of_interrest])

    for ppFile in ppListinRepo:
      if ppFile in commit_of_interest:

       file_with_path = os.path.join(repo_dir_absolute_path, ppFile)
       mapped_tuple = (file_with_path, each_commit)
       mappedPuppetList.append(mapped_tuple)

  return mappedPuppetList

def getChefRelatedCommits(repo_dir_absolute_path, chefListinRepo, branchName='master'):
  mappedChefList=[]
  track_exec_cnt = 0
  repo_  = Repo(repo_dir_absolute_path)
  all_commits = list(repo_.iter_commits(branchName))
  for each_commit in all_commits:
    track_exec_cnt = track_exec_cnt + 1

    cmd_of_interrest1 = "cd  " + repo_dir_absolute_path + " ; "
    cmd_of_interrest2 = "git show --name-status " + str(each_commit)  +  "  | awk '/.rb/ {print $2}'"
    cmd_of_interrest = cmd_of_interrest1 + cmd_of_interrest2
    commit_of_interest  = subprocess.check_output(['bash','-c', cmd_of_interrest])

    for chefFile in chefListinRepo:
      if chefFile in commit_of_interest:

       file_with_path = os.path.join(repo_dir_absolute_path, chefFile)
       mapped_tuple = (file_with_path, each_commit)
       mappedChefList.append(mapped_tuple)

  return mappedChefList

def getDiffStr(repo_path_p, commit_hash_p, file_p):
   
   cdCommand   = "cd " + repo_path_p + " ; "
   theFile     = os.path.relpath(file_p, repo_path_p)
   
   diffCommand = " git diff  " + commit_hash_p + " " + theFile + "  "
   command2Run = cdCommand + diffCommand
   diff_output = subprocess.check_output(['bash','-c', command2Run])

   return diff_output

def getCommitFullData(repo_path_param, repo_branch_param, pupp_commits_mapping):
  trac_exec_count = 0 
  pupp_bug_list = []
  for tuple_ in pupp_commits_mapping:
    file_ = tuple_[0]
    commit_ = tuple_[1]
    msg_commit =  commit_.message 

    msg_commit = msg_commit.replace('\n', ' ')
    msg_commit = msg_commit.replace(',',  ';')    
    msg_commit = msg_commit.replace('\t', ' ')
    msg_commit = msg_commit.replace('&',  ';')  
    msg_commit = msg_commit.replace('#',  ' ')
    msg_commit = msg_commit.replace('=',  ' ')      

    commit_hash = commit_.hexsha

    timestamp_commit = commit_.committed_datetime
    str_time_commit  = timestamp_commit.strftime('%Y-%m-%dT%H-%M-%S')

    diff_content_str = getDiffStr(repo_path_param, commit_hash, file_)

    tup_ = (repo_path_param, trac_exec_count, commit_hash, file_, str_time_commit, msg_commit, diff_content_str, repo_branch_param )
    pupp_bug_list.append(tup_)

    trac_exec_count += 1

  return pupp_bug_list

def constructDatasetForPuppet(orgParamName, repo_name_param, branchParam):
  
  repo_path   = "/Users/akond/PUPP_REPOS/" + orgParamName + "/" + repo_name_param
  repo_branch = branchParam

  all_pp_files_in_repo = getPuppetFilesOfRepo(repo_path)
  # print all_pp_files_in_repo
  
  rel_path_pp_files = getRelPathOfFiles(all_pp_files_in_repo, repo_path)
  # print rel_path_pp_files

  pupp_commits_in_repo = getPuppRelatedCommits(repo_path, rel_path_pp_files, repo_branch)
  # print pupp_commits_in_repo

  pupp_full_commit_data = getCommitFullData(repo_path, repo_branch, pupp_commits_in_repo)
  # print pupp_full_commit_data
  
  return pupp_full_commit_data 

def constructDatasetForChef(orgParamName, repo_name_param, branchParam):
  
  repo_path   = "/Users/akond/SECU_REPOS/" + orgParamName + "/" + repo_name_param
  repo_branch = branchParam

  all_chef_files_in_repo = getChefFilesOfRepo(repo_path)
  
  rel_path_chef_files = getRelPathOfFiles(all_chef_files_in_repo, repo_path)

  chef_commits_in_repo = getChefRelatedCommits(repo_path, rel_path_chef_files, repo_branch)

  chef_full_commit_data = getCommitFullData(repo_path, repo_branch, chef_commits_in_repo)
  
  return chef_full_commit_data 


def dumpContentIntoFile(strP, fileP):
  fileToWrite = open( fileP, 'w')
  fileToWrite.write(strP )
  fileToWrite.close()
  return str(os.stat(fileP).st_size)

def dumpDataAsStr(dic_p, fil_p): 
    csv_str = ''
    for proj, proj_data in dic_p.iteritems():
        for data_tuple in proj_data:
            repo_path, count, commit_hash, file_, date_time, text_comm, diff_, repo_branch_param = data_tuple 
            print '='*25 + ':'*3 + str(count)   + ':'*3 + repo_path  + ':'*3 + commit_hash + ':'*3 + 'START!' + '='*25
            print file_ 
            print '*'*10
            print diff_
            print '*'*10
            print text_comm
            print '*'*10
            print 'DECISION===>:'
            print '*'*10
            print '='*25 + ':'*3 + str(count) + ':'*3 + date_time + ':'*3 + 'END!!!' + '='*25    
            csv_str = csv_str + repo_path + ',' + str(count) + ',' + commit_hash + ',' + file_ + ',' + date_time + ',' + text_comm + '\n'      
    csv_str = 'REPO,COUNT,COMMIT,FILE,TIME,MESSAGE' + '\n' + csv_str
    dumpContentIntoFile(csv_str, fil_p)


if __name__=='__main__':
    '''
    Puppet dataset contruction 
    '''
    # orgName='wikimedia-downloads'
    # out_fil_nam = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/WIKI_PUPP_COMM.PKL'

    # orgName='openstack-downloads'
    # out_fil_nam = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/OSTK_PUPP_COMM.PKL'

    # fileName     = "/Users/akond/PUPP_REPOS/" + orgName + '/'+'eligible_repos.csv'
    # elgibleRepos = getEligibleProjects(fileName)
    # dic = {}
    # for proj_ in elgibleRepos:
    #     proj_data = constructDatasetForPuppet(orgName, proj_, 'master')
    #     dic[proj_] = proj_data

    '''
    Chef  dataset contruction 
    '''

    orgName='ostk-chef'
    out_fil_nam = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/OSTK_CHEF_COMM.PKL'

    fileName     = "/Users/akond/SECU_REPOS/" + orgName + '/'+'eligible_repos.csv'
    elgibleRepos = getEligibleProjects(fileName)
        
    dic = {}
    for proj_ in elgibleRepos:
        proj_data = constructDatasetForChef(orgName, proj_, 'master')
        dic[proj_] = proj_data


    pickle.dump( dic, open( out_fil_nam , 'wb')) 
    dumpDataAsStr(dic, out_fil_nam + '.csv')