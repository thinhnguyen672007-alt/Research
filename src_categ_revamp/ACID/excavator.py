'''
Akond Rahman 
Dec 02, 2018 
Mar 19, 2019: ACID: Extractor 
'''
import os 
import csv 
import numpy as np
import sys
from git import Repo
import  subprocess
import time 
import  datetime 
import _pickle as pickle 
from nltk.tokenize import sent_tokenize
import constants
import classifier
import hglib  # reff: https://www.mercurial-scm.org/wiki/PythonHglib
import re

# reload(sys)
# sys.setdefaultencoding(constants.ENCODING) 


def getEligibleProjects(fileNameParam):
  repo_list = []
  with open(fileNameParam, constants.FILE_READ_MODE) as f:
    reader = csv.reader(f)
    for row in reader:
      repo_list.append(row[0])
  return repo_list

def getPuppetFilesOfRepo(repo_dir_absolute_path):
    pp_, non_pp = [], []
    for root_, dirs, files_ in os.walk(repo_dir_absolute_path):
       for file_ in files_:
           full_p_file = os.path.join(root_, file_)
           if((os.path.exists(full_p_file)) and (constants.AST_PATH not in full_p_file) ):
             if (full_p_file.endswith(constants.PP_EXTENSION)):
               pp_.append(full_p_file)
    return pp_

def getRelPathOfFiles(all_pp_param, repo_dir_absolute_path):
  common_path = repo_dir_absolute_path
  files_relative_paths = [os.path.relpath(path, common_path) for path in all_pp_param]
  return files_relative_paths 

def getPuppRelatedCommits(repo_dir_absolute_path, ppListinRepo, branchName=constants.MASTER_BRANCH):
  mappedPuppetList=[]
  track_exec_cnt = 0
  repo_  = Repo(repo_dir_absolute_path)
  all_commits = list(repo_.iter_commits(branchName))
  for each_commit in all_commits:
    track_exec_cnt = track_exec_cnt + 1

    cmd_of_interrest1 = constants.CHANGE_DIR_CMD + repo_dir_absolute_path + " ; "
    cmd_of_interrest2 = constants.GIT_COMM_CMD_1 + str(each_commit)  +  constants.GIT_COMM_CMD_2
    cmd_of_interrest = cmd_of_interrest1 + cmd_of_interrest2
    commit_of_interest  = str(subprocess.check_output([constants.BASH_CMD, constants.BASH_FLAG, cmd_of_interrest])) #in Python 3 subprocess.check_output returns byte


    for ppFile in ppListinRepo:
      # print(ppFile, commit_of_interest)
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

def dumpDiffText(commit_repo_path, commit_hash, file_, diff_content_str, text_comm, date_time):
    dump_str = ''
    dump_str = dump_str + '='*25 + ':'*3  + commit_repo_path  + ':'*3 + commit_hash + ':'*3 + 'START!' + '='*25
    dump_str = dump_str +  file_ 
    dump_str = dump_str +  '*'*10 + '\n'
    dump_str = dump_str +  text_comm
    dump_str = dump_str +  '*'*10 + '\n'
    dump_str = dump_str +  'DECISION===>:'
    dump_str = dump_str +  '*'*10
    dump_str = dump_str +  '='*25 + ':'*3   + date_time + ':'*3 + 'END!!!' + '='*25    
    # print dump_str 

def analyzeCommit(repo_path_param, repo_branch_param, pupp_commits_mapping):
  verbose = False   # For oracle dataset it is True (later), otherwise it is False 
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

    # '''
    # for testing purpose , uncomment only for tool accuracy purpose 
    # '''
    # if commit_hash in constants.ORACLE_HASH_CHECKLIST:
    #   verbose = True 
    # else:
    #   verbose = False 
    # '''
    # ''' 

    timestamp_commit = commit_.committed_datetime
    str_time_commit  = timestamp_commit.strftime(constants.DATE_TIME_FORMAT) ## date with time 

    diff_content_str = getDiffStr(repo_path_param, commit_hash, file_)

    #### categorization zone 
    per_commit_defect_categ_list = []
    if (commit_hash not in hash_tracker):
      bug_status, index_status = classifier.detectBuggyCommit(msg_commit, verbose) 
      # print bug_status 
      if (bug_status) or (classifier.detectRevertedCommit(msg_commit) ):
        processed_message = processMessage(msg_commit)
        # each commit has multiple messages, need to merge them together in one list here, not in classifier 
        for tokenized_msg in processed_message:
            bug_categ = classifier.detectCateg(tokenized_msg, diff_content_str, verbose)
            per_commit_defect_categ_list.append(  bug_categ )
            # if verbose:
            #   print tokenized_msg
            #   print commit_hash, bug_categ, repo_path_param, str_time_commit
            #   print '-'*100   
      else:
        per_commit_defect_categ_list  = [ constants.NO_DEFECT_CATEG ]

      bug_categ_list = np.unique(  per_commit_defect_categ_list  )
      '''
      for testing purpose , uncomment only for tool accuracy purpose 
      '''
      # if verbose:
      #   print bug_categ_list
      '''
      '''
      if (len(bug_categ_list) > 0):
        for bug_categ_ in bug_categ_list:      
            tup_ = (commit_hash, bug_categ_, repo_path_param, str_time_commit) 
            all_defect_categ_list.append(tup_)  
            # print tup_[0], tup_[1], tup_[2], tup_[3]
            # print '-'*25
      else:    
            tup_ = (commit_hash, constants.NO_DEFECT_CATEG, repo_path_param, str_time_commit) 
            all_defect_categ_list.append(tup_)  
      hash_tracker.append(commit_hash) 
    #### file to hash mapping zone 
    if commit_hash not in all_commit_file_dict:
        all_commit_file_dict[commit_hash] = [file_]
    else:
        all_commit_file_dict[commit_hash]  = all_commit_file_dict[commit_hash] + [file_]    

  return all_commit_file_dict, all_defect_categ_list 

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


def analyzeHgCommit(repo_path_param, repo_branch_param, pupp_commits_mapping):
  pupp_bug_list = []
  all_commit_file_dict  = {}
  all_defect_categ_list = []
  hash_tracker = []
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
    if (commit_hash not in hash_tracker):
      bug_status, index_status = classifier.detectBuggyCommit(msg_commit) 
      if (bug_status) or (classifier.detectRevertedCommit(msg_commit) ):
        processed_message = processMessage(msg_commit)
        for tokenized_msg in processed_message:
            bug_categ = classifier.detectCateg(tokenized_msg, diff_content_str)
            per_commit_defect_categ_list.append(  bug_categ )
      else:
        per_commit_defect_categ_list  = [ constants.NO_DEFECT_CATEG ]

      bug_categ_list = np.unique(  per_commit_defect_categ_list  )
      if (len(bug_categ_list) > 0):
        for bug_categ_ in bug_categ_list:      
            tup_ = (commit_hash, bug_categ_, repo_path_param, str_time_commit) 
            # print tup_ 
            all_defect_categ_list.append(tup_)  
      else:    
            tup_ = (commit_hash, constants.NO_DEFECT_CATEG, repo_path_param, str_time_commit) 
            all_defect_categ_list.append(tup_)  
      hash_tracker.append(commit_hash) 
    #### file to hash mapping zone 
    if commit_hash not in all_commit_file_dict:
        all_commit_file_dict[commit_hash] = [commit_file]
    else:
        all_commit_file_dict[commit_hash]  = all_commit_file_dict[commit_hash] + [commit_file]    

  return all_commit_file_dict, all_defect_categ_list 

def runMiner(orgParamName, repo_name_param, branchParam):
  
  repo_path   = constants.ROOT_PUPP_DIR + orgParamName + "/" + repo_name_param
  repo_branch = branchParam

  if 'mozilla' in orgParamName:
    bashCommand= constants.CHANGE_DIR_CMD + repo_path  + constants.HG_REV_SPECL_CMD 
    repo_complete = hglib.open(repo_path)
    files = list(repo_complete.manifest())
    pp_files =getHgLegitFiles(files)
    all_commits = repo_complete.log()
    pupp_commits_in_repo = getHgPuppetCommitMapping(all_commits, pp_files, bashCommand)
    commit_file_dict, categ_defect_list = analyzeHgCommit(repo_path, repo_branch, pupp_commits_in_repo)
  else:
    all_pp_files_in_repo = getPuppetFilesOfRepo(repo_path)  
    rel_path_pp_files = getRelPathOfFiles(all_pp_files_in_repo, repo_path)
    pupp_commits_in_repo = getPuppRelatedCommits(repo_path, rel_path_pp_files, repo_branch)
    commit_file_dict, categ_defect_list = analyzeCommit(repo_path, repo_branch, pupp_commits_in_repo)
    # print 'Commit count:', len(commit_file_dict) 
  return commit_file_dict, categ_defect_list

  

def dumpContentIntoFile(strP, fileP):
  fileToWrite = open( fileP, constants.FILE_WRITE_MODE)
  fileToWrite.write(strP )
  fileToWrite.close()
  return str(os.stat(fileP).st_size)

