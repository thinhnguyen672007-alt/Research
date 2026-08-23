'''
Script to inser data in table 
Akond Rahman 
Dec 24, 2018 
'''

import pymysql.cursors
import cPickle as pickle
import os, csv, random


def giveConnection():
    _host = "localhost"
    _user = ""
    _password = ""
    _database = ""
    # Connect to the database
    _connection = pymysql.connect(host=_host,
                                 user=_user,
                                 password=_password,
                                 db=_database,
                                 cursorclass=pymysql.cursors.DictCursor)
    return _connection

def insertTableValues(tableName, path, content, hash_, message):
  connection = giveConnection()
  try:
    with connection.cursor() as cursor:
      tableFieldStr = tableName +  "(repo_path, diff_content, diff_hash, diff_message)"
      inseSttmt = "INSERT INTO " + tableFieldStr +" VALUES (%s, %s, %s, %s)"
      dataToInserTuple = (path, content, hash_, message)
      cursor.execute(inseSttmt, dataToInserTuple)
      connection.commit()
  finally:
    connection.close()


def insertIntoDiffTable(file_name):
    pkl_dic = pickle.load(open(file_name, 'rb'))    
    for k_, v_ in pkl_dic.iteritems():
        for tup in v_:
            repo_path = tup[0]
            diff_cont = tup[6]
            diff_hash = tup[2]
            diff_mesg = tup[5]

            tableName = 'categ_diff' 

            insertTableValues(tableName, repo_path, diff_cont, diff_hash, diff_mesg)


def createAssiFile( IBD_File):
        ass_data  = []
        with open(IBD_File, 'rU') as file_:
             reader_ = csv.reader(file_)
             next(reader_, None)
             for row_ in reader_:
                 studentID  = str(519) + str(row_[0].split('_')[-1])
                 chefID     = int (row_[1].split('L')[1] ) + 350 
                 ansiID     = int (row_[2].split('L')[1] ) + 350 
                 ass_data.append((studentID, chefID))
                 ass_data.append((studentID, ansiID))        
        counter = 0
        prevStudent = -999
        for dat in ass_data:
            if prevStudent != int(dat[0]):
               counter = 0
               prevStudent = int(dat[0])
            else: 
               counter += 1 
            print  str(dat[1]) +  ',' + dat[0] + ','  +  str(counter)

if __name__=='__main__':
    '''
    Populate categ_diff table 
    '''
#    diffFile1='OSTK_PUPP_COMM.PKL'
#    diffFile2='WIKI_PUPP_COMM.PKL' 

#    insertIntoDiffTable(diffFile1)   
#    insertIntoDiffTable(diffFile2)    
# 

    '''
    Populate categ_assiggnment table 
    '''

    # create assignment CSV for database 
    # createAssiFile('/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/oracle_work/IBD_DATA.csv')
 