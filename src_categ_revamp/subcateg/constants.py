'''
Akond Rahman 
Mar 19, 2019 
ACID: Store configuration strings and cosntants here 
'''

ROOT_PUPP_DIR  = '/Users/akond/ICSE2020_PUPP_REPOS/' 
REPO_FILE_LIST = 'eligible_repos.csv'
MASTER_BRANCH  = 'master' 
FILE_READ_MODE = 'rU' 
AST_PATH = 'EXTRA_AST' 
PP_EXTENSION = '.pp'
DATE_TIME_FORMAT = "%Y-%m-%dT%H-%M-%S"
WHITE_SPACE  = ' '
TAB = '\t'
NEWLINE = '\n'
HASH_SYMBOL = '#'

CHANGE_DIR_CMD = 'cd '
GIT_COMM_CMD_1 = "git show --name-status "
GIT_COMM_CMD_2 = "  | awk '/.pp/ {print $2}'" 
BASH_CMD = 'bash'
BASH_FLAG = '-c'
GIT_DIFF_CMD = " git diff  "
HG_REV_SPECL_CMD   = " ; hg log -p -r " 

ENCODING = 'utf8'
UTF_ENCODING = 'utf-8'
FILE_WRITE_MODE = 'w'
SPACY_ENG_DICT  = 'en_core_web_sm'
ROOT_TOKEN = 'ROOT'

STR_LIST_BOUNDS  = 3 # tri-grams 
NO_DEFECT_CATEG        = 'NO_DEFECT'
CONFIG_DEFECT_CATEG    = 'CONFIG_DEFECT'
DEP_DEFECT_CATEG       = 'DEP_DEFECT'
DOC_DEFECT_CATEG       = 'DOC_DEFECT'
IDEM_DEFECT_CATEG      = 'IDEM_DEFECT'
CONDI_DEFECT_CATEG     = 'CONDI_DEFECT'
SECU_DEFECT_CATEG      = 'SECU_DEFECT'
BLD_DEFECT_CATEG       = 'BUILD_DEFECT'
DB_DEFECT_CATEG        = 'DB_DEFECT' 
INSTALL_DEFECT_CATEG   = 'INSTALL_DEFECT' 
LOGGING_DEFECT_CATEG   = 'LOG_DEFECT'
NETWORK_DEFECT_CATEG   = 'NET_DEFECT'
RACE_DEFECT_CATEG      = 'RACE_DEFECT'
SERVICE_DEFECT_CATEG   = 'SERVICE_DEFECT'
SYNTAX_DEFECT_CATEG    = 'SYNTAX_DEFECT'

prem_bug_kw_list      = ['error', 'bug', 'fix', 'issue', 'mistake', 'incorrect', 'fault', 'defect', 'flaw', 'solve' ]
# config_defect_kw_list = ['connection', 'string', 'paramet', 'hash', 'value', 'config', 'field', 'option', 'version', 'url', 'setting', 'ip', 'repo', 'link', 'time', 'server', 'command', 'setting', 'hiera', 'data', 'sql', 'permiss', 'mode', 'dir', 'protocol', 'missing', 'reference', 'path', 'location', 'driver', 'port', 'protocol', 'gateway', 'tcp', 'udp', 'fact', 'id']
config_defect_kw_list = ['value', 'config', 'option',  'setting', 'hiera', 'data' ]
# dep_defect_kw_list    = ['requir', 'depend', 'relation', 'order', 'sync', 'compatibility', 'ordering', 'missing', 'ensure', 'packag', 'conflict', 'name', 'inherit', 'module', 'merge', 'namespace', 'test', 'includ']
dep_defect_kw_list    = ['requir', 'depend', 'relation', 'order', 'sync', 'compatibil', 'ensure',  'inherit'] 
doc_defect_kw_list    = ['doc', 'comment', 'spec', 'license', 'copyright', 'notice', 'header', 'readme'] 
idem_defect_kw_list   = ['idempot']
logic_defect_kw_list  = ['logic', 'condition', 'bool']
# secu_defect_kw_list   = ['vulnerability', 'ssl', 'firewall', 'secret', 'authenticate', 'tls', 'ca_file', 'password', 'security', 'cve']
secu_defect_kw_list   = ['vulnerab', 'ssl', 'secr', 'authenti', 'password', 'security', 'cve']

# build_defect_kw_list  = ['build']
# db_defect_kw_list     = ['db', 'database', 'databas']
# insta_defect_kw_list  = ['install']
# race_defect_kw_list   = ['race']
logging_defect_kw_list= ['log']
# network_defect_kw_list= ['provis', 'provision', 'network', 'l23', 'balancer', 'domain', 'route', 'proxy', 'dhcp']
network_defect_kw_list= ['provis', 'network', 'proxy', 'dhcp']
# service_defect_kw_list= ['install', 'race', 'build', 'service', 'caching', 'backend', 'job', 'start', 'gate', 'stage', 'env', 'requirement', 'restore', 'server']
service_defect_kw_list= ['race', 'build', 'service', 'requirement', 'restore', 'server']

# syntax_defect_kw_list = ['compil', 'class', 'lint', 'warn', 'clean', 'typo', 'comma', 'style', 'wrong', 'quote', 'cosmetic', 'compil', 'variable', 'spelling', 'declar', 'missing', 'indent', 'definition', 'regex', 'type', 'format', 'duplicat', 'deprecate', 'parameter', 'outdate', 'variabl']
syntax_defect_kw_list = ['compil', 'lint', 'warn', 'typo', 'spell', 'indent', 'regex', 'duplicat', 'variabl', 'whitespac']

# EXTRA_SYNTAX_KW       = ['definition', 'role', 'whitespace', 'parameter', 'lint', 'style', 'typo', 'variable', 'indent', 'test', 'pattern', 'duplicate'] 
# EXTRA_CONFIG_KW       = ['url', 'version', 'config', 'sql', 'tcp', 'hiera', 'repo', 'vlan', 'connection']  
# EXTRA_DEPENDENCY_KW   = ['dep', 'ensur', 'requir', 'modul', 'packag']  
# EXTRA_SERVICE_KW      = ['test', 'setup', 'site', 'restart', 'deploy', 'start', 'driver']  
# EXTRA_DOCU_KW         = ['readme', 'doc', 'comment', 'license'] 
EXTRA_FIX_KEYWORD     = 'fix'   
# EXTRA_SOLVE_KEYWORD   = 'solve'
EXTRA_BUG_KEYWORD     = 'bug'   

DFLT_KW         = 'default'
CLOSE_KW        = 'closes-bug'
MERGE_KW        = 'merge' 
REVERT_KW       = 'revert'
REVERT_REGEX    = r'^revert.*\".*\"'

IDEM_XTRA_KW    = 'idempot' # for detectBuggyCommit() 

LOGIC_XTRA_KW1  = 'condit'
LOGIC_XTRA_KW2  = 'logic'
LOGIC_XTRA_KW3  = 'bool' 

SYNTAX_XTRA_KW1 = 'lint'
SYNTAX_XTRA_KW2 = 'typo' # for detectBuggyCommit() 
# SYNTAX_XTRA_KW3 = 'spac'
SYNTAX_XTRA_KW4 = 'syntax'

DOC_XTRA_KW     = 'notice' 
# DEPEND_XTRA_KW  = 'override' 
# NETWORK_XTRA_KW = 'provis'

diff_config_code_elems = ['hiera' , 'hash', 'parameter']
VAR_SIGN = '='
ATTR_SIGN = '=>'
diff_depen_code_elems = ['~>' , '::', 'include', 'packag', 'exec']
diff_logic_code_elems = ['if' , 'unless', 'els', 'case']
diff_secu_code_elems  = ['tls', 'cert', 'cred', 'ssl', 'password', 'pass', 'pwd'] 
diff_service_code_elems = ['service'] 
# diff_syntax_code_elems = ['class']
diff_idem_code_elem    = 'class' 
diff_idem_removal_cnt  = 10 

diff_extra_idem_elems  = ['ensure', 'unless', 'creates', 'replace'] 

lev_cutoff = 75

'''
Oracle dataset work 
'''
ORACLE_HASH_CHECKLIST = ['75e460ab929a76e9e4a8d42740a529b3a476e952', 
                         '9a5a540738f887f87886ae4f9f52d5ade1b26bc7', 
                         '0d834093814b3d184eff36b2835530a847ee6421', 
                         '854e0e7b9fc339dc56bf3e2b3de7107c3f35b835', 
                         'a7dedf197a24bf8a3fad00d1d1f58eede2f43057',
                         '114536ef2e7c569300019844e0ca57d278e27791'
                        ]