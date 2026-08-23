'''
Mar 20, 2019 
Akond Rahman 
Classify commit messages
'''
import constants 
import diff_parser

from nltk.tokenize import sent_tokenize
import re 
import spacy 
spacy_engine = spacy.load(constants.SPACY_ENG_DICT)
import future 
import numpy as np 
from nltk.stem.porter import *
stemmerObj = PorterStemmer()



def checkForNum(str_par):
    return any(char_.isdigit() for char_ in str_par)

def filterCommitMessage(msg_par):
    temp_msg_    = msg_par.lower()
    splitted_msg = temp_msg_.split(constants.WHITE_SPACE)
    splitted_msg = [stemmerObj.stem(x_) for x_ in splitted_msg] ##porter stemming , x_ is a string 
    splitted_msg = [x_ for x_ in splitted_msg if len(x_) > 1 ]  ## remove special characterers , x_ is a string 
    # splitted_msg = [x_ for x_ in splitted_msg if x_.isalnum() ]  ## remove special characterers , x_ is a string 
    filtered_msg = [x_ for x_ in splitted_msg if checkForNum(x_) == False ] ## remove alphanumeric characters , x_ is a string     

    return filtered_msg 

def doDepAnalysis(msg_par):
    msg_to_analyze = []
    filtered_msg = filterCommitMessage(msg_par)
    unicode_msg_ = constants.WHITE_SPACE.join(filtered_msg)
    try:
        unicode_msg  = unicode(unicode_msg_, constants.UTF_ENCODING)
    except: 
        unicode_msg = unicode_msg_
    # print unicode_msg 
    spacy_doc = spacy_engine(unicode_msg)
    for token in spacy_doc:
        if (token.dep_ == constants.ROOT_TOKEN): 
            for x_ in token.children:
                msg_to_analyze.append(x_.text)
    return constants.WHITE_SPACE.join(msg_to_analyze) 


def doTempCleanUp(msg_str):

    msg_ = msg_str.replace(constants.CLOSE_KW, constants.WHITE_SPACE)
    msg_ = msg_.replace(constants.MERGE_KW, constants.WHITE_SPACE)
    msg_ = msg_.replace(constants.DFLT_KW, constants.WHITE_SPACE)    

    return msg_

def detectBuggyCommit(msg_, verboseFlag = False):
    flag2ret  = False 
    index2ret = 0
    msg_ = msg_.lower()

    if (constants.IDEM_XTRA_KW in msg_) or (constants.SYNTAX_XTRA_KW2 in msg_):
        msg_ = doTempCleanUp(msg_)


    # if(any(x_ in msg_ for x_ in constants.prem_bug_kw_list)) and ( constants.DFLT_KW not in msg_) and ( constants.CLOSE_KW not in msg_) and (constants.MERGE_KW not in msg_) :  ## this gives too mnay false negatives   
    if(any(x_ in msg_ for x_ in constants.prem_bug_kw_list)) and ( constants.DFLT_KW not in msg_) and (constants.MERGE_KW not in msg_) :    
        str2see = [y_ for y_ in constants.prem_bug_kw_list][0]
        index2ret = msg_.find( str2see  ) 
        flag2ret = True 
    return flag2ret, index2ret

def detectRevertedCommit(msg_):
    flag2ret  = False 
    msg_ = msg_.lower()
    revert_matches = re.findall(constants.REVERT_REGEX, msg_)
    if(len(revert_matches) > 0):
        flag2ret = True 
    return flag2ret

'''
detectCateg takes a sentence and a diff from a commit message as input , and return a defect category (single value)
'''
def detectCateg(msg_, diff_, verboseFlag=False): 
    temp_msg_ = '' ## for oracle dataset 
    defect_categ_to_ret = constants.NO_DEFECT_CATEG 
    if (len(diff_) > 0):
        temp_msg_list = filterCommitMessage(msg_) # for extra false negative rules 
        temp_msg_     = constants.WHITE_SPACE.join(temp_msg_list) # for extra false negative rules 
        
        # if verboseFlag:
        #     print 'Originally was:',  msg_
        #     print 'Now becomes:', temp_msg_
        msg_       = doDepAnalysis(msg_) ## depnding on results, this extra step of dependnecy parsing may change 
        # print 'Dependency analysis output:', msg_ 
        # diff_parse_dict = diff_parser.parseTheDiff(diff_) 
        # print 'Lines is the diff:', len(diff_parse_dict) 
        
        # if(any(x_ in msg_ for x_ in constants.syntax_defect_kw_list )) or (diff_parser.checkDiffForSyntaxDefects(diff_)): 
        #     defect_categ_to_ret = constants.SYNTAX_DEFECT_CATEG 
        # if(any(x_ in msg_ for x_ in constants.syntax_defect_kw_list )) : #more restriictive rule  
        #     defect_categ_to_ret = constants.SYNTAX_DEFECT_CATEG 
        # else:
        #     if(any(x_ in msg_ for x_ in constants.dep_defect_kw_list)) or (diff_parser.checkDiffForDepDefects(diff_)): 
        #         defect_categ_to_ret = constants.DEP_DEFECT_CATEG 
        #     if(any(x_ in msg_ for x_ in constants.doc_defect_kw_list )) or (diff_parser.checkDiffForDocDefects(diff_)) : 
        #         defect_categ_to_ret = constants.DOC_DEFECT_CATEG 
        #     if(any(x_ in msg_ for x_ in constants.idem_defect_kw_list )) or (diff_parser.checkDiffForIdempotenceDefects(diff_) or (diff_parser.checkDiffForIdemWithAttr(diff_)) ): 
        #         defect_categ_to_ret = constants.IDEM_DEFECT_CATEG 
        #     # if(any(x_ in msg_ for x_ in constants.logic_defect_kw_list )) or (diff_parser.checkDiffForLogicDefects(diff_)) : 
        #     #     defect_categ_to_ret = constants.CONDI_DEFECT_CATEG 
        #     if(any(x_ in msg_ for x_ in constants.logic_defect_kw_list )) and (diff_parser.checkDiffForLogicDefects(diff_)) : #more restricitve
        #         defect_categ_to_ret = constants.CONDI_DEFECT_CATEG 
        #     # if(any(x_ in msg_ for x_ in constants.secu_defect_kw_list )) or (diff_parser.checkDiffForSecurityDefects(diff_)) : 
        #     #     defect_categ_to_ret = constants.SECU_DEFECT_CATEG 
        #     if(any(x_ in msg_ for x_ in constants.secu_defect_kw_list ))  : # more restrictive rule  
        #         defect_categ_to_ret = constants.SECU_DEFECT_CATEG 
        #     if(any(x_ in msg_ for x_ in constants.logging_defect_kw_list )) or (diff_parser.checkDiffForServiceDefects(diff_)) : 
        #         defect_categ_to_ret = constants.LOGGING_DEFECT_CATEG 
        #     if(any(x_ in msg_ for x_ in constants.network_defect_kw_list )) or (diff_parser.checkDiffForServiceDefects(diff_)): 
        #         defect_categ_to_ret = constants.NETWORK_DEFECT_CATEG 
        #     if(any(x_ in msg_ for x_ in constants.service_defect_kw_list )) or (diff_parser.checkDiffForServiceDefects(diff_)): 
        #         defect_categ_to_ret = constants.SERVICE_DEFECT_CATEG 
        #     if(any(x_ in msg_ for x_ in constants.config_defect_kw_list)) or (diff_parser.checkDiffForConfigDefects(diff_)): 
        #         defect_categ_to_ret =  constants.CONFIG_DEFECT_CATEG                 

        if(any(x_ in msg_ for x_ in constants.syntax_defect_kw_list )) : #more restriictive rule  
            defect_categ_to_ret = constants.SYNTAX_DEFECT_CATEG 
        else:
            if(any(x_ in msg_ for x_ in constants.dep_defect_kw_list))  or (diff_parser.checkDiffForDepDefects(diff_) and (constants.EXTRA_FIX_KEYWORD in temp_msg_  )  ): 
                defect_categ_to_ret = constants.DEP_DEFECT_CATEG 
            if(any(x_ in msg_ for x_ in constants.doc_defect_kw_list )) or (diff_parser.checkDiffForDocDefects(diff_) and (constants.EXTRA_FIX_KEYWORD in temp_msg_  )  ): 
                defect_categ_to_ret = constants.DOC_DEFECT_CATEG 
            if(any(x_ in msg_ for x_ in constants.idem_defect_kw_list )): 
                defect_categ_to_ret = constants.IDEM_DEFECT_CATEG 
            if(any(x_ in msg_ for x_ in constants.logic_defect_kw_list )): 
                defect_categ_to_ret = constants.CONDI_DEFECT_CATEG 
            if(any(x_ in msg_ for x_ in constants.secu_defect_kw_list )): 
                defect_categ_to_ret = constants.SECU_DEFECT_CATEG 
            if(any(x_ in msg_ for x_ in constants.logging_defect_kw_list )): 
                defect_categ_to_ret = constants.LOGGING_DEFECT_CATEG 
            if(any(x_ in msg_ for x_ in constants.network_defect_kw_list )) : 
                defect_categ_to_ret = constants.NETWORK_DEFECT_CATEG 
            if(any(x_ in msg_ for x_ in constants.service_defect_kw_list )) or ( diff_parser.checkDiffForServiceDefects(diff_) and (constants.EXTRA_FIX_KEYWORD in temp_msg_  )  ): 
                defect_categ_to_ret = constants.SERVICE_DEFECT_CATEG 
            if(any(x_ in msg_ for x_ in constants.config_defect_kw_list)) or ( (diff_parser.checkDiffForConfigDefects(diff_)) and (constants.EXTRA_FIX_KEYWORD in temp_msg_  )): 
                defect_categ_to_ret =  constants.CONFIG_DEFECT_CATEG                 

        # extra rule for idempotence 
        if ( constants.IDEM_XTRA_KW in temp_msg_ ) and ( constants.EXTRA_FIX_KEYWORD in temp_msg_ ):
            defect_categ_to_ret = constants.IDEM_DEFECT_CATEG 

        # extra rule for conditional 
        if (( constants.LOGIC_XTRA_KW1 in temp_msg_ ) or ( constants.LOGIC_XTRA_KW2 in temp_msg_ ) or ( constants.LOGIC_XTRA_KW3 in temp_msg_ ) ) and ( constants.EXTRA_FIX_KEYWORD in temp_msg_ ):
            defect_categ_to_ret =  constants.CONDI_DEFECT_CATEG 

        # extra rule for syntax 
        if (( constants.SYNTAX_XTRA_KW1 in temp_msg_ ) or ( constants.SYNTAX_XTRA_KW2 in temp_msg_ ) or ( constants.SYNTAX_XTRA_KW4 in temp_msg_ ) ) and (( constants.EXTRA_FIX_KEYWORD in temp_msg_ )  ):
            defect_categ_to_ret = constants.SYNTAX_DEFECT_CATEG 

        # extra rule for doc 
        if ( constants.DOC_XTRA_KW in temp_msg_  ) and ( constants.EXTRA_FIX_KEYWORD in temp_msg_ ):
            defect_categ_to_ret = constants.DOC_DEFECT_CATEG 

        # # extra rule for dep
        # if ( constants.DEPEND_XTRA_KW in temp_msg_  ) and ( constants.EXTRA_FIX_KEYWORD in temp_msg_ ):
        #     defect_categ_to_ret = constants.DEP_DEFECT_CATEG 

        # # extra rule for provisioning
        # if ( constants.NETWORK_XTRA_KW in temp_msg_  ) and ( constants.EXTRA_FIX_KEYWORD in temp_msg_ ):
        #     defect_categ_to_ret = constants.NETWORK_DEFECT_CATEG 

    return defect_categ_to_ret 