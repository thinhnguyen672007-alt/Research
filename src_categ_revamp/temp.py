import pandas as pd 
import csv 
import os 
import numpy as np 

def dumpContentIntoFile(strP, fileP):
    fileToWrite = open( fileP, 'w')
    fileToWrite.write(strP)
    fileToWrite.close()
    return str(os.stat(fileP).st_size)


if __name__=='__main__':
    file_2018 = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/2018_repos.csv'
    file_2019 = '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/2019_repos.csv'    


    df_2018 = pd.read_csv(file_2018)
    df_2019 = pd.read_csv(file_2019)    

    repos_2018 = df_2018['name'].tolist() 
    repos_2019 = np.unique( df_2019['link'].tolist()  )
    repos_2019 = [x_.split('/')[-2] + '/' + x_.split('/')[-1] for x_ in repos_2019 ]

    missing_repos = [x_ for x_ in repos_2019 if x_ not in repos_2018] 

    print 'Missing repos:', len(missing_repos) 

    str_ = ''
    for x_ in missing_repos:
        str_ = str_ + x_ + ',' + '\n' 
    str_ = 'Repo' + '\n' + str_
    dumpContentIntoFile(str_, '/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/Extra_2019_repos.csv')