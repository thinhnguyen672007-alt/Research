'''
Get metrics for repos 
Akond Rahman 
April 12, 2019 
'''
import csv 
import numpy as np
import sys
from git import Repo
import  subprocess
import time 
import  datetime 
import os 
import cPickle as pickle 
import pandas as pd 
from scipy.stats import entropy
import math 
from collections import Counter
import hglib

def getPuppetFilesOfRepo(repo_dir_absolute_path):
    pp_, non_pp = [], []
    for root_, dirs, files_ in os.walk(repo_dir_absolute_path):
       for file_ in files_:
           full_p_file = os.path.join(root_, file_)
           if((os.path.exists(full_p_file)) and ('EXTRA_AST' not in full_p_file) ):
             if (full_p_file.endswith('.pp')):
               pp_.append(full_p_file)
    return pp_



def getRelPathOfFiles(all_pp_param, repo_dir_absolute_path):
  common_path = repo_dir_absolute_path
  files_relative_paths = [os.path.relpath(path, common_path) for path in all_pp_param]
  return files_relative_paths 

def getPuppRelatedHgCommits(repo_dir_absolute_path, ppListinRepo, branchName='master'):
  mappedPuppetList=[]
  repo_complete = hglib.open(repo_dir_absolute_path)
  all_commits = repo_complete.log()
  for each_commit in all_commits:
      commit_hash = each_commit[1]
      commit_ts   = each_commit[-1] 
      str_time_commit  = commit_ts.strftime('%Y-%m-%dT%H-%M-%S')    
      diffCommand = 'cd ' + repo_dir_absolute_path + ' ; hg log -p -r ' + commit_hash + ' ; '
      diff_output = subprocess.check_output([ 'bash' , '-c', diffCommand])

      for legitFile in ppListinRepo:
        if legitFile in diff_output:
          file_with_path = os.path.join(repo_dir_absolute_path, legitFile)
          mapped_tuple = (file_with_path, str(commit_hash), str_time_commit )
          mappedPuppetList.append(mapped_tuple)
  return mappedPuppetList


def getPuppRelatedCommits(repo_dir_absolute_path, ppListinRepo, branchName='master'):
  mappedPuppetList=[]
  track_exec_cnt = 0
  repo_  = Repo(repo_dir_absolute_path)
  all_commits = list(repo_.iter_commits(branchName))
  for each_commit in all_commits:
    track_exec_cnt = track_exec_cnt + 1

    cmd_of_interrest1 = "cd " + repo_dir_absolute_path + " ; "
    cmd_of_interrest2 = "git show --name-status " + str(each_commit)  +  "  | awk '/.pp/ {print $2}'" 
    cmd_of_interrest = cmd_of_interrest1 + cmd_of_interrest2
    commit_of_interest  = subprocess.check_output(['bash' , '-c', cmd_of_interrest])

    for ppFile in ppListinRepo:
      if ppFile in commit_of_interest:

       file_with_path = os.path.join(repo_dir_absolute_path, ppFile)
       mapped_tuple = (file_with_path, each_commit)
       mappedPuppetList.append(mapped_tuple)

  return mappedPuppetList

def getDiffStr(repo_path_p, commit_hash_p, file_p):
   
   cdCommand   = "cd " + repo_path_p + " ; "
   theFile     = os.path.relpath(file_p, repo_path_p)
   
   diffCommand = " git diff  " + commit_hash_p + " " + theFile + " "
   command2Run = cdCommand + diffCommand
   diff_output = subprocess.check_output(['bash', '-c', command2Run])

   return diff_output

def getHgDiffStr(repo_path_p, commit_hash_p, file_p):
   
   cdCommand   = "cd " + repo_path_p + " ; "
   theFile     = os.path.relpath(file_p, repo_path_p)
   
   diffCommand = " hg log -p -r   " + commit_hash_p +  " "
   command2Run = cdCommand + diffCommand
   diff_output = subprocess.check_output(['bash', '-c', command2Run])

   return diff_output

def getDiffLOC(diff_text):
    add_cnt, del_cnt = 0, 0 
    diff_text_list = diff_text.split('\n') 
    diff_text_list = [x_ for x_ in diff_text_list if (('---' not in x_) and ('+++' not in x_)) ]
    add_text_list  = [x_ for x_ in diff_text_list if x_.startswith('+')]
    del_text_list  = [x_ for x_ in diff_text_list if x_.startswith('-')]

    # print add_text_list, del_text_list 
    add_cnt, del_cnt = len(add_text_list), len(del_text_list)
    return add_cnt, del_cnt 

def getDevCountForFile(param_file_path, repo_path):
   author_count      = 1 

   cdCommand         = "cd " + repo_path + " ; "
   theFile           = os.path.relpath(param_file_path, repo_path)
   commitCountCmd    = " git blame "+ theFile +"  | awk '{print $2}' | cut -d'(' -f2 "
   command2Run = cdCommand + commitCountCmd

   commit_count_output = subprocess.check_output(['bash','-c', command2Run])
   author_count_output = commit_count_output.split('\n')
   author_count_output = [x_ for x_ in author_count_output if x_!='']
   author_count        = len(np.unique(author_count_output))

   return author_count

def getHgDevCountForFile(param_file_path, repo_path):
   author_count      = 1 

   cdCommand         = "cd " + repo_path + " ; "
   theFile           = os.path.relpath(param_file_path, repo_path)
   commitCountCmd    = "hg churn --diffstat  " + theFile + " | awk '{print $1}'  "
   command2Run = cdCommand + commitCountCmd 

   commit_count_output = subprocess.check_output(['bash','-c', command2Run])
   author_count_output = commit_count_output.split('\n')
   author_count_output = [x_ for x_ in author_count_output if x_!='']
   author_count = len(np.unique(author_count_output))

   return author_count

def getDevsOfRepo(repo_path_param):
   commit_dict       = {}
   author_dict       = {}

   cdCommand         = "cd " + repo_path_param + " ; "
   commitCountCmd    = " git log --pretty=format:'%H_%an' "
   command2Run = cdCommand + commitCountCmd

   commit_count_output = subprocess.check_output(['bash','-c', command2Run])
   author_count_output = commit_count_output.split('\n')
   for commit_auth in author_count_output:
       commit_ = commit_auth.split('_')[0]
       
       author_ = commit_auth.split('_')[1]
       author_ = author_.replace(' ', '')
       # only one author for one commit 
       if commit_ not in commit_dict:
           commit_dict[commit_] = author_ 
       # one author can be involved with multiple commits 
       if author_ not in author_dict:
           author_dict[author_] = [commit_] 
       else:            
           author_dict[author_] = author_dict[author_] + [commit_] 
   return commit_dict, author_dict   

def getDevsOfHgRepo(repo_path_param):
   commit_dict       = {}
   author_dict       = {}
   
   repo_complete = hglib.open(repo_path_param)  
   all_commits = repo_complete.log() 
   for commit in all_commits:
       author_ = str(commit.author)
       commit_ = str(commit.rev) 
       # only one author for one commit 
       if commit_ not in commit_dict:
           commit_dict[commit_] = author_ 
       # one author can be involved with multiple commits 
       if author_ not in author_dict:
           author_dict[author_] = [commit_] 
       else:            
           author_dict[author_] = author_dict[author_] + [commit_] 
   return commit_dict, author_dict   


def mineCommitsOfTheRepo(repo_path_param, repo_branch_param, pupp_commits_mapping, dev_commit_dict):
    commit_time_dict = {} 
    all_commit_metrics = []

    for tuple_ in pupp_commits_mapping:
        file_ = tuple_[0]
        commit_ = tuple_[1]
        msg_commit =  commit_.message 
        commit_hash = commit_.hexsha

        timestamp_commit = commit_.committed_datetime
        str_time_commit  = timestamp_commit.strftime('%Y-%m-%dT%H-%M-%S')

        diff_content_str = getDiffStr(repo_path_param, commit_hash, file_)
        loc_add, loc_del = getDiffLOC(diff_content_str) 
        loc_tot          = loc_add + loc_del 

        dir_             = os.path.dirname(file_) 
        devs_for_file    = getDevCountForFile(file_, repo_path_param) 
        if commit_hash in dev_commit_dict:
          committer_name   = dev_commit_dict[commit_hash] 
        else:
          committer_name   = 'TEMP'

        metric_tuple = (commit_hash, file_, dir_, repo_path_param, loc_add, loc_del, loc_tot, devs_for_file, committer_name, str_time_commit)  
        # print metric_tuple
        all_commit_metrics.append(metric_tuple) 
        # to get recent experience 
        if commit_hash not in commit_time_dict:
          commit_time_dict[commit_hash] = str_time_commit 
    
    commit_metric_df = pd.DataFrame(all_commit_metrics, columns=['COMMIT_HASH', 'FILE', 'DIR', 'REPO', 'LOC_ADD', 'LOC_DEL', 'LOC_TOT', 'DEVS_FILE', 'AUTHOR_NAME_FILE', 'TIME']) 
    return commit_metric_df , commit_time_dict 

def mineCommitsOfTheHgRepo(repo_path_param, repo_branch_param, pupp_commits_mapping, dev_commit_dict):
    commit_time_dict = {} 
    all_commit_metrics = []

    for tuple_ in pupp_commits_mapping:
        file_       = tuple_[0]
        commit_hash = tuple_[1]
        str_time_commit  = tuple_[2]

        diff_content_str = getHgDiffStr(repo_path_param, commit_hash, file_)
        loc_add, loc_del = getDiffLOC(diff_content_str) 
        loc_tot          = loc_add + loc_del 

        dir_             = os.path.dirname(file_) 
        devs_for_file    = getHgDevCountForFile(file_, repo_path_param) 
        if commit_hash in dev_commit_dict:
          committer_name   = dev_commit_dict[commit_hash] 
        else:
          committer_name   = 'TEMP'

        metric_tuple = (commit_hash, file_, dir_, repo_path_param, loc_add, loc_del, loc_tot, devs_for_file, committer_name, str_time_commit)  
        # print metric_tuple
        all_commit_metrics.append(metric_tuple) 
        # to get recent experience 
        if commit_hash not in commit_time_dict:
          commit_time_dict[commit_hash] = str_time_commit 
    
    commit_metric_df = pd.DataFrame(all_commit_metrics, columns=['COMMIT_HASH', 'FILE', 'DIR', 'REPO', 'LOC_ADD', 'LOC_DEL', 'LOC_TOT', 'DEVS_FILE', 'AUTHOR_NAME_FILE', 'TIME']) 
    return commit_metric_df , commit_time_dict

def calcSpread(loc_list):
    if len(loc_list) > 0:
      entr_ = round(entropy(loc_list) , 5)        
    else:
      entr_ = float(0) 
    if (math.isnan(entr_)):
      entr_ = float(0)       
    return entr_ 

def getDevsExp(auth_name, auth_dict):
  exp_ = float(0)
  print auth_name 
  print auth_dict 
  print '='*10
  if auth_name in auth_dict:
    auth_commits = auth_dict[auth_name] 
    exp_ = len(auth_commits) 
  return exp_
    
def calcRecentExp(commit_year_list):
    recent_exp_final = 0 

    year_list = [int(x_) for x_ in commit_year_list ]
    dict_ = dict(Counter(year_list)) 
    unique_years = list(np.unique(year_list)) 
    unique_years.sort(reverse = True) 
    recent_exp_list = []
    for year_index in xrange(len(unique_years)):
        year_ = unique_years[year_index] 
        contribs = dict_[year_] 
        recent_exp = float(contribs) / float(year_index + 1)
        recent_exp_list.append(recent_exp) 
    recent_exp_final = round(sum(recent_exp_list) , 5) 

    return recent_exp_final 


def getDevsRecentExp(auth_name, auth_dict, time_dict):
  recent_exp_ = float(0)
  if auth_name in auth_dict:
    auth_commits     = auth_dict[auth_name] # get all commits for the author 
    commit_time_list = [time_dict[x_] for x_ in auth_commits if x_ in time_dict] # get the timestamp for all commits for author
    commit_year_list = [x_.split('T')[0].split('-')[0] for x_ in commit_time_list]  # get the year for all commits for author
    recent_exp_      = calcRecentExp(commit_year_list) # pass the year list to func 
  return recent_exp_

def finalizeMetrics(df_pa, dev_commit_p, time_dict):
  commit_metric_list    = []
  commit_hash_list = np.unique( df_pa['COMMIT_HASH'].tolist() )
  print dev_pa.head()
  for hash_ in commit_hash_list:
    hash_df             = df_pa[df_pa['COMMIT_HASH']==hash_]
    dev_name            = hash_df['AUTHOR_NAME_FILE'].tolist()[0]

    per_hash_files      = len( np.unique( hash_df['FILE'].tolist() ) )
    per_hash_dirs       = len( np.unique(hash_df['DIR'].tolist() ) )
    
    per_hash_loc_list   = hash_df['LOC_TOT'].tolist() 
    per_hash_tot_loc    = sum(per_hash_loc_list) 
    
    per_hash_spread     = calcSpread(per_hash_loc_list) 
    
    per_hash_devs_list  = hash_df['DEVS_FILE'].tolist() 
    per_hash_devs       = sum(per_hash_devs_list)

    per_hash_devs_exp   = getDevsExp(dev_name, dev_commit_p) 

    per_hash_devs_rexp  = getDevsRecentExp(dev_name, dev_commit_p, time_dict)  

    metric_tuple        = ( hash_, per_hash_files, per_hash_dirs, per_hash_tot_loc, per_hash_spread, per_hash_devs, per_hash_devs_exp, per_hash_devs_rexp )
    commit_metric_list.append(metric_tuple) 
  
  return commit_metric_list 


def getBranchName(proj_):
    branch_name = ''
    proj_branch = {'biemond@biemond-oradb':'puppet4_3_data', 'derekmolloy@exploringBB':'version2', 'exploringBB':'version2', 
                'jippi@puppet-php':'php7.0', 'maxchk@puppet-varnish':'develop', 'threetreeslight@my-boxen':'mine', 
                'puppet':'production'
              } 
    if proj_ in proj_branch:
        branch_name = proj_branch[proj_]
    else:
        branch_name = 'master'
    return branch_name

def runMiner(orgParamName, repo_name_param, branchParam):
  
  repo_path   = '/Users/akond/ICSE2020_PUPP_REPOS/' + orgParamName + "/" + repo_name_param
  print repo_path
  repo_branch = getBranchName(repo_name_param)

  if 'mozilla-releng' in orgParamName:
    all_devs_in_repo, dev_commit_repo = getDevsOfHgRepo(repo_path)  
    all_pp_files_in_repo = getPuppetFilesOfRepo(repo_path)  
    rel_path_pp_files = getRelPathOfFiles(all_pp_files_in_repo, repo_path)
    pupp_commits_in_repo = getPuppRelatedHgCommits(repo_path, rel_path_pp_files, repo_branch)
    metric_df, time_comm_dict = mineCommitsOfTheHgRepo(repo_path, repo_branch, pupp_commits_in_repo, all_devs_in_repo)   
  else:
    all_devs_in_repo, dev_commit_repo = getDevsOfRepo(repo_path)  
    all_pp_files_in_repo = getPuppetFilesOfRepo(repo_path)  
    rel_path_pp_files = getRelPathOfFiles(all_pp_files_in_repo, repo_path)
    pupp_commits_in_repo = getPuppRelatedCommits(repo_path, rel_path_pp_files, repo_branch)
    metric_df, time_comm_dict = mineCommitsOfTheRepo(repo_path, repo_branch, pupp_commits_in_repo, all_devs_in_repo) 

  all_commit_all_metrics = finalizeMetrics(metric_df, dev_commit_repo, time_comm_dict)   

  return all_commit_all_metrics 

def getPuppFilesNHashes(orgParamName, repo_name_param, branchParam):
  fileHashList = []
  repo_path   = '/Users/akond/ICSE2020_PUPP_REPOS/' + orgParamName + "/" + repo_name_param
  print 'Processing:', repo_path
  repo_branch = getBranchName(repo_name_param)
  all_pp_files_in_repo = getPuppetFilesOfRepo(repo_path)  
  rel_path_pp_files = getRelPathOfFiles(all_pp_files_in_repo, repo_path)


  if 'mozilla-releng' in orgParamName:
    pupp_commits_in_repo = getPuppRelatedHgCommits(repo_path, rel_path_pp_files, repo_branch)
  else:
    pupp_commits_in_repo = getPuppRelatedCommits(repo_path, rel_path_pp_files, repo_branch)
  for tup_ in pupp_commits_in_repo:
    fileHashList.append( (tup_[1], tup_[0]) )

  return fileHashList


def getGitDevEmailsOfRepo(repo_path_param):
   per_repo_emails = []
   cdCommand         = "cd " + repo_path_param + " ; "
   commitCountCmd    = " git log --pretty=format:'%H_%aE' " # E for email, n for name 
   command2Run = cdCommand + commitCountCmd

   commit_count_output = subprocess.check_output(['bash','-c', command2Run])
   author_count_output = commit_count_output.split('\n')
   for commit_auth in author_count_output:
       commit_ = commit_auth.split('_')[0]       
       author_ = commit_auth.split('_')[1]
       author_ = author_.replace(' ', '')
       print repo_path_param + ',' + author_ 
       per_repo_emails.append(author_) 
   return per_repo_emails

def getAuthorOfHash(hash_p, repo_p): 
   # reff: https://stackoverflow.com/questions/29876342/how-to-get-only-author-name-or-email-in-git-given-sha1
   author_emails = []

   cdCommand         = "cd " + repo_p + " ; "
   commitCountCmd    = " git show -s --format='%ae' " + hash_p 
   command2Run = cdCommand + commitCountCmd

   commit_count_output = subprocess.check_output(['bash','-c', command2Run])
   author_count_output = commit_count_output.split('\n')

   author_emails = [x_ for x_ in author_count_output if '@' in x_] 

   return author_emails
 