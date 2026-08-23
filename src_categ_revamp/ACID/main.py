'''
Akond Rahman 
Mar 19, 2019 : Tuesday 
ACID: Main 
'''
import excavator
import constants
import pandas as pd 
# import cPickle as pickle
import _pickle as pickle 
import time
import datetime


'''
This script goes to each repo and mines commits and commit messages and then get the defect category 
'''
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


def giveTimeStamp():
  tsObj = time.time()
  strToret = datetime.datetime.fromtimestamp(tsObj).strftime('%Y-%m-%d %H:%M:%S')
  return strToret

if __name__=='__main__':

    t1 = time.time()
    print('Started at:', giveTimeStamp()) 
    print('*'*100)
    # orgName     = 'oracle-dataset'
    # out_fil_nam = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/closed-coding-2019/ORACLE_DATASET_COMM.PKL'
    # out_csv_fil = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/closed-coding-2019/ORACLE_CATEG_OUTPUT_SEMIFINAL.csv'
    # out_pkl_fil = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/closed-coding-2019/ORACLE_CATEG_OUTPUT_SEMIFINAL.PKL'

    # orgName='ghub-downloads'
    # out_fil_nam = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/GHUB_PUPP_COMM.PKL'
    # out_csv_fil = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/GHUB_CATEG_OUTPUT_FINAL.csv'
    # out_pkl_fil = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/GHUB_CATEG_OUTPUT_FINAL.PKL'

    # orgName='wikimedia-downloads'
    # out_fil_nam = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/WIKI_PUPP_COMM.PKL'
    # out_csv_fil = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/WIKI_CATEG_OUTPUT_FINAL.csv'
    # out_pkl_fil = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/WIKI_CATEG_OUTPUT_FINAL.PKL'

    # orgName     = 'mozilla-releng-downloads'
    # out_fil_nam = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/MOZI_PUPP_COMM.PKL'
    # out_csv_fil = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/MOZI_CATEG_OUTPUT_FINAL.csv'
    # out_pkl_fil = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/MOZI_CATEG_OUTPUT_FINAL.PKL'

    # orgName='openstack-downloads'
    # out_fil_nam = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/OSTK_PUPP_COMM.PKL'
    # out_csv_fil = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/OSTK_CATEG_OUTPUT_FINAL.csv'
    # out_pkl_fil = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/OSTK_CATEG_OUTPUT_FINAL.PKL'    

    orgName='test-repos'
    out_fil_nam = '/Users/arahman/Documents/OneDriveWingUp/OneDrive-TennesseeTechUniversity/Research/IaC/iac-ncsu/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/TEST_ONLY.PKL'
    out_csv_fil = '/Users/arahman/Documents/OneDriveWingUp/OneDrive-TennesseeTechUniversity/Research/IaC/iac-ncsu/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/TEST_ONLY_CATEG_OUTPUT_FINAL.csv'
    out_pkl_fil = '/Users/arahman/Documents/OneDriveWingUp/OneDrive-TennesseeTechUniversity/Research/IaC/iac-ncsu/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/TEST_ONLY_CATEG_OUTPUT_FINAL.PKL' 

    fileName     = constants.ROOT_PUPP_DIR + orgName + '/' + constants.REPO_FILE_LIST 
    elgibleRepos = excavator.getEligibleProjects(fileName)
    dic   = {}
    categ = [] 
    for proj_ in elgibleRepos:
        branchName = getBranchName(proj_) 
        per_proj_commit_dict, per_proj_full_defect_list = excavator.runMiner(orgName, proj_, branchName)
        categ = categ + per_proj_full_defect_list 
        # print proj_ , len(per_proj_full_defect_list) 
        print('Finished analyzing:', proj_)
        dic[proj_] = (per_proj_commit_dict, per_proj_full_defect_list) 
        print('='*50)  
    
    all_proj_df = pd.DataFrame(categ) 
    all_proj_df.to_csv(out_csv_fil, header=['HASH','CATEG','REPO','TIME'], index=False) 

    with open(out_pkl_fil, 'wb') as fp_:
        pickle.dump(dic, fp_)  
    print('*'*100)
    print('Ended at:', giveTimeStamp())
    print('*'*100)
    t2 = time.time()
    time_diff = round( (t2 - t1 ) / 60, 5) 
    print("Duration: {} minutes".format(time_diff))
    print('*'*100)   

        
