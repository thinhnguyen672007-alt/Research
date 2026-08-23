'''
Named entity recognition 
'''
# import nltk
# from nltk.tag import StanfordNERTagger
# #reff-1: https://medium.com/explore-artificial-intelligence/introduction-to-named-entity-recognition-eda8c97c2db1
# #reff-2: https://nlp.stanford.edu/software/CRF-NER.html#Download


# print 'NTLK Version:', nltk.__version__
# stanford_ner_tagger = StanfordNERTagger(
#     '/Users/akond/stanford_ner/' + 'english.muc.7class.distsim.crf.ser.gz',
#     '/Users/akond/stanford_ner/' + 'stanford-ner.jar'
# )


# article = '''Asian shares skidded on Tuesday after a rout in tech stocks put Wall Street to the sword, while 
# a sharp drop  in oil prices and political risks in Europe pushed the dollar to 16-month highs as investors dumped riskier assets. 
# MSCI's broadest index of Asia-Pacific shares outside Japan dropped 1.7 percent to a 1-1/2 week trough, with Australian shares sinking 1.6 
# percent. Sterling fell to $1.286 after three straight sessions of losses took it to the lowest since Nov.1 as there were still considerable 
# unresolved issues with the European Union over Brexit, British Prime Minsiter Theresa May said on Monday.'''

# results = stanford_ner_tagger.tag(article.split())
# for result in results:
#     tag_value = result[0]
#     tag_type = result[1]
#     if tag_type != 'O':
#         print 'Type: {}, Value: {}'.format ( tag_type, tag_value )
#         print '-'*50



# '''
# Dependnecy parsing 
# '''
# import spacy
# import future 
# #reff: https://spacy.io/usage/linguistic-features

# nlp = spacy.load('en_core_web_sm')
# doc = nlp(u"Autonomous cars shift insurance liability toward manufacturers")
# doc = nlp(u"Change section name for AMQP rabbit parameters  Parameter 'amqp_durable_queues' under section 'DEFAULT' now is deprecated since Liberty and should be placed under certain rpc backend section [1;2]  [1] https://github.com/openstack/oslo.messaging/blob/liberty/oslo_messaging/_drivers/amqp.py L36 [2] http://docs.openstack.org/liberty/config-reference/content/configuring-rpc.html  Change-Id: Ib7bbea586b21c42eb9fd13c4a376d23fce165272 ")
# for token in doc:
#     print(token.text, token.dep_, token.head.text, token.head.pos_,
#           [child for child in token.children])

'''
Dependency parsing setup for ACID 
Akond Rahman 
Mar 17, 2019 
'''
import pandas as pd 
from nltk.tokenize import sent_tokenize
import re 
import spacy 
spacy_engine = spacy.load('en_core_web_sm')
import future 
import numpy as np 
from nltk.tag import StanfordNERTagger
stanford_ner_tagger = StanfordNERTagger(
    '/Users/akond/stanford_ner/' + 'english.muc.7class.distsim.crf.ser.gz',
    '/Users/akond/stanford_ner/' + 'stanford-ner.jar'
)

def removeHash(mess):
    '''
    removes hash 
    '''
    # out_mes   = re.sub(r'^[a-f0-9]{40}(:.+)?$', '', mess) ## not working 
    out_mes   = re.sub(r'[a-f0-9]{40}(:.+)?$', '', mess) ##  working 
    splitted_str = out_mes.split(' ')
    splitted_str = [x_ for x_ in splitted_str if len(x_) > 1 ]
    splitted_str = [x_.replace(':', '') for x_ in splitted_str if len(x_) > 1 ]
    final_str = ' '.join(splitted_str)
    return final_str 

def doDepAnalysis(msg_par, commit_hash, commit_repo):
    unicode_msg = ''
    try:
       unicode_msg  = unicode(msg_par, 'utf-8')
       spacy_doc = spacy_engine(unicode_msg)
       for token in spacy_doc:
        if (token.dep_ == 'ROOT') and (token.text == 'fix'):
            print '='*50 
            print commit_repo              
            print '-'*10 
            print commit_hash             
            print '-'*10 
            print msg_par
            print '-'*10 
            print unicode_msg
            print '-'*10 
            print(token.text, token.dep_, token.head.text, token.head.pos_, [x_ for x_ in token.children])  
            print '='*50 
    except: 
        print 'Unicode error!'


    # print spacy_doc.print_tree()
    # for chunk_ in spacy_doc.noun_chunks:
    #     print chunk_.root.text, chunk_.root.dep_ , chunk_.text   


def doNERAnalysis(msg_par):
    print msg_par
    results = stanford_ner_tagger.tag(msg_par.split())
    for result in results:
        tag_value = result[0]
        tag_type = result[1]
        if tag_type == 'O':
            print 'Type: {}, Value: {}'.format ( tag_type, tag_value )
            print '-'*50

def detectBuggyCommitMessages(msg_lis, hash_, repo_):
    prem_kw_list = ['error', 'bug', 'fix', 'issue', 'mistake', 'incorrect', 'fault', 'defect', 'flaw' ]
    # print msg_lis
    # https://towardsdatascience.com/named-entity-recognition-with-nltk-and-spacy-8c4a7d88e7da
    for msg_ in msg_lis:
        msg_ = msg_.lower()
        if(any(x_ in msg_ for x_ in prem_kw_list)) and ('default' not in msg_) and ('closes-bug' not in msg_):
            msg_ = removeHash(msg_)
            doDepAnalysis(msg_, hash_, repo_)
            # doNERAnalysis(msg_)

def processMessage(indi_comm_mess, hash_, repo_):
    if ('*' in indi_comm_mess):
       splitted_messages = indi_comm_mess.split('*')
    else:
       splitted_messages = sent_tokenize(indi_comm_mess)
    # print splitted_messages 
    detectBuggyCommitMessages(splitted_messages, hash_, repo_) 
    


def processMessages(comm_df):
    comm_hash_list =  np.unique( comm_df['HASH'].tolist() )
    for comm_ in comm_hash_list:
        per_comm_df = comm_df[comm_df['HASH']==comm_]
        comm_mess   = per_comm_df['MESSAGE'].tolist()[0]
        comm_repo   = per_comm_df['REPO'].tolist()[0]
        processMessage(comm_mess, comm_, comm_repo)  

if __name__=='__main__':
    comm_mess_file='/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/dataset/OSTK_PUPP_ONLY_DEFE_COMM.csv'
    comm_mess_df  = pd.read_csv(comm_mess_file)

    processMessages(comm_mess_df)