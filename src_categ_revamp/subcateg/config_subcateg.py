'''
Akond Rahman 
Aug 04, 2019 
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
from nltk.tokenize import sent_tokenize
import hglib  
import re
import pandas as pd 

import constants

reload(sys)
sys.setdefaultencoding( 'utf-8' ) 

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

def getPuppetFilesOfRepo(repo_dir_absolute_path):
    pp_, non_pp = [], []
    for root_, dirs, files_ in os.walk(repo_dir_absolute_path):
       for file_ in files_:
           full_p_file = os.path.join(root_, file_)
           if((os.path.exists(full_p_file)) and ('EXTRA_AST'  not in full_p_file) ):
             if (full_p_file.endswith('.pp')):
               pp_.append(full_p_file)
    return pp_

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

    cmd_of_interrest1 = constants.CHANGE_DIR_CMD + repo_dir_absolute_path + " ; "
    cmd_of_interrest2 = constants.GIT_COMM_CMD_1 + str(each_commit)  +  constants.GIT_COMM_CMD_2
    cmd_of_interrest = cmd_of_interrest1 + cmd_of_interrest2
    commit_of_interest  = subprocess.check_output([constants.BASH_CMD, constants.BASH_FLAG, cmd_of_interrest])

    for ppFile in ppListinRepo:
      if ppFile in commit_of_interest:

       file_with_path = os.path.join(repo_dir_absolute_path, ppFile)
       mapped_tuple = (file_with_path, each_commit)
       mappedPuppetList.append(mapped_tuple)

  return mappedPuppetList

def getDiffStr(repo_path_p, commit_hash_p, file_p):
   
   cdCommand   = constants.CHANGE_DIR_CMD + repo_path_p + " ; "
   theFile     = os.path.relpath(file_p, repo_path_p)
   
   diffCommand = constants.GIT_DIFF_CMD + commit_hash_p + constants.WHITE_SPACE + theFile + constants.WHITE_SPACE
   command2Run = cdCommand + diffCommand
   diff_output = subprocess.check_output([constants.BASH_CMD, constants.BASH_FLAG, command2Run])

   return diff_output

def makeDepParsingMessage(m_, i_): 
    upper, lower  = 0, 0
    lower = i_ - constants.STR_LIST_BOUNDS
    upper = i_ + constants.STR_LIST_BOUNDS 
    if upper > len(m_):
      upper = - 1 
    if lower < 0:
      lower = 0
    return constants.WHITE_SPACE.join(m_[i_ - constants.STR_LIST_BOUNDS : i_ + constants.STR_LIST_BOUNDS])

def processMessage(indi_comm_mess):
    splitted_messages = []
    if ('*' in indi_comm_mess):
       splitted_messages = indi_comm_mess.split('*')
    else:
       splitted_messages = sent_tokenize(indi_comm_mess)
    return splitted_messages 

def getIndiSubCateg(message_):
  message_ = message_.lower() 
  sub_categ = 'NETWORK_CONFIG_DEFECT'
  '''
  (i) for data storage systems such as Amazon S3, Elastisearch, MySQL, MongDB, Openstack Swift, and SQLite; 
  (ii) for file system issues such as specifying file permissions and file names; 
  (iii) networking such as TCP/DHCP ports and addresses, MAC addresses, and IP table rules; 
  (iv) for user credentials such as usernames and passwords; and 
  (v) caching systems such as Memcached. 
  '''
  # if ('s3' in message_ or 'elastisearch' in message_ or 'sql' in message_ or 'db' in message_ or 'database'in message_ ):
  if ('sql' in message_ or 'db' in message_ or 'database'in message_ ):
    sub_categ = 'DATASTORAGE_CONFIG_DEFECT'
  elif ('file' in message_ or 'disk' in message_ or 'path' in message_ or 'dir' in message_):
    sub_categ = 'FILESYSTEM_CONFIG_DEFECT'
  elif ('network' in message_ or 'router' in message_ or 'port' in message_ or 'address' in message_ or 'dns' in message_ or 'dhcp' in message_ or 'tcp' in message_):
    sub_categ = 'NETWORK_CONFIG_DEFECT'    
  elif ('password' in message_ or 'name' in message_ or 'cred' in message_ or 'user' in message_ or 'auth' in message_):
    sub_categ = 'CREDENTIAL_CONFIG_DEFECT'    
  elif ('cache' in message_ ):
    sub_categ = 'CACHE_CONFIG_DEFECT'    
  return sub_categ

def reportGitSubCateg(repo_path_param, repo_branch_param, pupp_commits_mapping, config_hash_list):
  pupp_bug_list = []
  all_commit_file_dict  = {}
  all_defect_categ_list = []
  hash_tracker = []
  for tuple_ in pupp_commits_mapping:

    file_ = tuple_[0]
    commit_ = tuple_[1]
    msg_commit =  commit_.message 

    msg_commit = msg_commit.replace('\n', constants.WHITE_SPACE)
    msg_commit = msg_commit.replace(',',  ';')    
    msg_commit = msg_commit.replace('\t', constants.WHITE_SPACE)
    msg_commit = msg_commit.replace('&',  ';')  
    msg_commit = msg_commit.replace('#',  constants.WHITE_SPACE)
    msg_commit = msg_commit.replace('=',  constants.WHITE_SPACE)      

    commit_hash = commit_.hexsha
    timestamp_commit = commit_.committed_datetime
    str_time_commit  = timestamp_commit.strftime(constants.DATE_TIME_FORMAT) 

    #### subcategorization zone 
    per_commit_defect_categ_list = []
    if (commit_hash in config_hash_list):
        processed_message = processMessage(msg_commit)
        for tokenized_msg in processed_message:
            # print tokenized_msg
            bug_categ = getIndiSubCateg(tokenized_msg)
            per_commit_defect_categ_list.append(  bug_categ )

    bug_categ_list = np.unique(  per_commit_defect_categ_list  )
    if (len(bug_categ_list) > 0):
        for bug_categ_ in bug_categ_list:      
            tup_ = (commit_hash, bug_categ_, repo_path_param, str_time_commit) 
            all_defect_categ_list.append(tup_)  

  return all_defect_categ_list 

def getHgLegitFiles(fileListParam):
  outputList = []
  for file_ in fileListParam:
    tmp_ = file_[4] 
    if constants.PP_EXTENSION in tmp_:
      outputList.append(tmp_)
  return outputList

def getHgPuppetCommitMapping(all_commits_param, legit_files_param, bashCommand):
  listToRet = []
  for e in  all_commits_param:
    commit_hash = e[1]
    timestamp   = e[-1]
    message     = e[-2]
    diffCommand = bashCommand + commit_hash #reff: https://stackoverflow.com/questions/5376642/mercurial-diffs-in-a-particular-changeset
    diff_output = subprocess.check_output([ constants.BASH_CMD , constants.BASH_FLAG, diffCommand])

    for legitFile in legit_files_param:
      if(legitFile in diff_output):
        tmp_tup = (commit_hash, legitFile, timestamp, message, diff_output)
        listToRet.append(tmp_tup)
  return listToRet


def reportMerSubCateg(repo_path_param, repo_branch_param, pupp_commits_mapping, config_hash_list):
  pupp_bug_list = []
  all_defect_categ_list = []
  full_str_for_sanity = ''
  for tuple_ in pupp_commits_mapping:

    commit_hash      = tuple_[0]
    commit_file      = tuple_[1]
    timestamp_commit = tuple_[2]
    str_time_commit  = timestamp_commit.strftime(constants.DATE_TIME_FORMAT)    
    msg_commit       = tuple_[3] 

    msg_commit = msg_commit.replace('\n', constants.WHITE_SPACE)
    msg_commit = msg_commit.replace(',',  ';')    
    msg_commit = msg_commit.replace('\t', constants.WHITE_SPACE)
    msg_commit = msg_commit.replace('&',  ';')  
    msg_commit = msg_commit.replace('#',  constants.WHITE_SPACE)
    msg_commit = msg_commit.replace('=',  constants.WHITE_SPACE)      

    diff_content_str = tuple_[4]

    #### categorization zone 
    per_commit_defect_categ_list = []
    if (commit_hash in config_hash_list):
        processed_message = processMessage(msg_commit)
        for tokenized_msg in processed_message:
            bug_categ = getIndiSubCateg(tokenized_msg)
            per_commit_defect_categ_list.append(  bug_categ )

    bug_categ_list = np.unique(  per_commit_defect_categ_list  )
    if (len(bug_categ_list) > 0):
        for bug_categ_ in bug_categ_list:      
            tup_ = (commit_hash, bug_categ_, repo_path_param, str_time_commit) 
            # print tup_ 
            all_defect_categ_list.append(tup_)       

  return  all_defect_categ_list 

def runMiner(orgParamName, repo_name_param, branchParam, config_defect_list):
  
  repo_path   = constants.ROOT_PUPP_DIR + orgParamName + "/" + repo_name_param
  repo_branch = branchParam

  if 'mozilla' in orgParamName:
    bashCommand= constants.CHANGE_DIR_CMD + repo_path  + constants.HG_REV_SPECL_CMD 
    repo_complete = hglib.open(repo_path)
    files = list(repo_complete.manifest())
    pp_files =getHgLegitFiles(files)
    all_commits = repo_complete.log()
    pupp_commits_in_repo = getHgPuppetCommitMapping(all_commits, pp_files, bashCommand)
    categ_defect_list = reportMerSubCateg(repo_path, repo_branch, pupp_commits_in_repo, config_defect_list)
  else:
    all_pp_files_in_repo = getPuppetFilesOfRepo(repo_path)  
    rel_path_pp_files = getRelPathOfFiles(all_pp_files_in_repo, repo_path)
    pupp_commits_in_repo = getPuppRelatedCommits(repo_path, rel_path_pp_files, repo_branch)
    categ_defect_list = reportGitSubCateg(repo_path, repo_branch, pupp_commits_in_repo, config_defect_list)
  return categ_defect_list

  

def dumpContentIntoFile(strP, fileP):
  fileToWrite = open( fileP, constants.FILE_WRITE_MODE)
  fileToWrite.write(strP )
  fileToWrite.close()
  return str(os.stat(fileP).st_size)

def getBranchName(proj_):
    branch_name = ''
    proj_branch = {'biemond@biemond-oradb':'puppet4_3_data', 'derekmolloy@exploringBB':'version2', 'exploringBB':'version2', 
                   'jippi@puppet-php':'php7.0', 'maxchk@puppet-varnish':'develop', 'threetreeslight@my-boxen':'mine', 
                   'puppet':'production'
                  } 
    if proj_ in proj_branch:
        branch_name = proj_branch[proj_]
    else:
        branch_name = constants.MASTER_BRANCH
    return branch_name


if __name__=='__main__':

    t1 = time.time()
    print 'Started at:', giveTimeStamp()
    print '*'*100

    # orgName          = 'ghub-downloads'
    # out_csv_fil      = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/GHUB_CATEG_SUBCONFIG_FINAL.csv'
    # config_categ_fil = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/GHUB_CATEG_OUTPUT_FINAL.csv'    

    # orgName          = 'mozilla-releng-downloads'
    # out_csv_fil      = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/MOZI_CATEG_SUBCONFIG_FINAL.csv'
    # config_categ_fil = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/MOZI_CATEG_OUTPUT_FINAL.csv'    

    # orgName          = 'openstack-downloads'
    # out_csv_fil      = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/OSTK_CATEG_SUBCONFIG_FINAL.csv'
    # config_categ_fil = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/OSTK_CATEG_OUTPUT_FINAL.csv'

    orgName          = 'wikimedia-downloads'
    out_csv_fil      = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/WIKI_CATEG_SUBCONFIG_FINAL.csv'
    config_categ_fil = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/WIKI_CATEG_OUTPUT_FINAL.csv'

    fileName     = '/Users/akond/ICSE2020_PUPP_REPOS/'  + orgName + '/' + 'eligible_repos.csv'
    elgibleRepos = getEligibleProjects(fileName)
    dic   = {}
    categ = [] 
    for proj_ in elgibleRepos:
        branchName = getBranchName(proj_) 
        categ_df = pd.read_csv(config_categ_fil)
        config_categ_df = categ_df[categ_df['CATEG']=='CONFIG_DEFECT'] 
        config_categ_ls = np.unique( config_categ_df['HASH'].tolist() )
        per_proj_full_defect_list = runMiner(orgName, proj_, branchName, config_categ_ls)
        categ = categ + per_proj_full_defect_list 
        print 'For subcategories of configuration defects, finished analyzing:', proj_
        print '='*50 
    
    all_proj_df = pd.DataFrame(categ) 
    all_proj_df.to_csv(out_csv_fil, header=['HASH','CATEG','REPO','TIME'], index=False) 

    print '*'*100
    print 'Ended at:', giveTimeStamp()
    print '*'*100
    t2 = time.time()
    time_diff = round( (t2 - t1 ) / 60, 5) 
    print "Duration: {} minutes".format(time_diff)
    print '*'*100  