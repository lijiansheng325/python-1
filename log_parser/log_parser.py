# -*- coding: cp936 -*-
## function: remove file 
## remark: python version 2-7-3

import os
import sys
import shutil
import datetime
import time
import errno
import getopt

# clean tag to remove output directory
CLEAN_TAG = 1

# parser step
PARSER_STEP = 100000

# a size, b size is similar as 'grep -a5 -b5...'
a_size = -6
b_size = 5


ADB_FETCH_LOGS_CMD = "adb logcat -c && adb logcat -v threadtime"

PHONE_INFO_FILENANE = 'phone_info.txt'

REPORTS_PATH = './reports/'
TOP_RESULT_FILE = 'reports.txt'
CRASH_FILE = 'crash.txt'
ANR_FILE = 'anr.txt'
FC_FILE = 'fc.txt'
TC_FILE = 'tc.txt'
LOGCAT_FILE = 'logcat_snipest.txt'

ANR_PATH = "ANR"
SDCARD_SEMS_PATH = "SDCARD_SEM"
SDCARD_LOGS_PATH = "SDCARD_LOG"
DROPBOX_PATH = "DROP_BOX"
TOMBSTONES_PATH = "TOMB_STONE"

ANR_CMD = "adb pull /data/anr "
SDCARD_SEMS_CMD = "adb pull /sdcard/sems "
SDCARD_LOGS_CMD = "adb pull /sdcard/logs "
DROPBOX_CMD = "adb pull /data/system/dropbox "
TOMBSTONES_CMD = "adb pull /data/tombstones "

q = []
a_list=[]
b_list=[] 

# total result of current test
TOTAL_DICT = dict()

# catagorzied result of each kind of test
CRASH_SPLIT_DICT = dict()
ANR_SPLIT_DICT = dict()
FC_SPLIT_DICT = dict()
TC_SPLIT_DICT = dict()

# detailed result of each kind of test
CRASH_DICT = dict()
ANR_DICT = dict()
FC_DICT = dict()
TC_DICT = dict()

# parser count of current test
parser_count = 0

TAG_DICT = { 
    "ANR_0": "Application is not responding",
    "ANR_1": "ANR in",
    "ANR_2": "APP_ANR happens",
    "CRASH": "CRASH",
    "FC": "FATAL EXCEPTION ",
    "TC": "Tombstone written to: /data/tombstones"   
}

def dump_dict(dict):
    for key in dict:
        print key + ':\n' + str(dict[key])

def increase_dict_value(dict, key):
    if (key in dict):
        dict[key] += 1
    else:
        dict[key] = 1

def append_dict_value(dict, key, value):
    if (key in dict):
        dict[key] += '\n\n'
        dict[key] += value
    else:
        dict[key] = value

def insert_result_to_detail_dict(tag_key, package_key, log_result):
    if tag_key == 'CRASH':
        append_dict_value(CRASH_DICT, package_key, log_result)
    elif tag_key =='ANR_0' or tag_key == 'ANR_1':
        append_dict_value(ANR_DICT, package_key, log_result)
    elif tag_key == 'FC':
        append_dict_value(FC_DICT, package_key, log_result)
    elif tag_key == 'TC':
        append_dict_value(TC_DICT, package_key, log_result)

def insert_result_to_split_dict(tag_key, package_key):
    if tag_key == 'CRASH':
        increase_dict_value(CRASH_SPLIT_DICT, package_key)        
    elif tag_key =='ANR_0' or tag_key == 'ANR_1':
        increase_dict_value(ANR_SPLIT_DICT, package_key)        
    elif tag_key == 'FC':
        increase_dict_value(FC_SPLIT_DICT, package_key)        
    elif tag_key == 'TC':
        increase_dict_value(TC_SPLIT_DICT, package_key)        

def insert_result_to_total_dict(tag_key):
    if tag_key == 'CRASH':
        increase_dict_value(TOTAL_DICT, 'CRASH')        
    elif tag_key =='ANR_0' or tag_key == 'ANR_1':
        increase_dict_value(TOTAL_DICT, 'ANR')        
    elif tag_key == 'FC':
        increase_dict_value(TOTAL_DICT, 'FC')        
    elif tag_key == 'TC':
        increase_dict_value(TOTAL_DICT, 'TC')        

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError:
        if os.path.exists(path):
            # We are nearly safe
            pass
        else:
            # There was an error on creation, so make sure we know about it
            raise

#def DumpTopResult(test_name):
#    dump_dict_to_file(test_name, TOP_RESULT_FILE, TOTAL_DICT)
#    dump_dict_to_file(test_name, TOP_RESULT_FILE, CRASH_SPLIT_DICT)    
#    dump_dict_to_file(test_name, TOP_RESULT_FILE, ANR_SPLIT_DICT)    
#    dump_dict_to_file(test_name, TOP_RESULT_FILE, FC_SPLIT_DICT)    
#    dump_dict_to_file(test_name, TOP_RESULT_FILE, TC_SPLIT_DICT)        

#def dump_dict_to_file(test_name, file_name, dict_name):
#    path_name = test_name
#    filepath = os.path.join(path_name, file_name)
#    if not os.path.exists(path_name):
#        os.makedirs(path_name)    
#    #make_sure_path_exists(path_name)
#
#    file_handler=open(filepath,'w+')
#    for key in dict_name:
#        file_handler.write(key)
#        file_handler.write(':')
#        file_handler.write(str(dict_name[key]))
#        file_handler.write('\n')
#    file_handler.close()

def dump_detail_dict_to_file(test_name, file_name, dict):
    path_name = test_name
    filepath = os.path.join(path_name, file_name)
    #if not os.path.exists(path_name):
    #    os.makedirs(path_name)    
    make_sure_path_exists(path_name)

    file_handler=open(filepath,'w+')
    for key in dict:
        file_handler.write(key)
        file_handler.write(':\n')
        file_handler.write(str(dict[key]))
        file_handler.write('\n\n')    
    file_handler.close()

def DumpDetailResult(test_name):
    dump_detail_dict_to_file(test_name, CRASH_FILE, CRASH_DICT)    
    dump_detail_dict_to_file(test_name, ANR_FILE, ANR_DICT)    
    dump_detail_dict_to_file(test_name, FC_FILE, FC_DICT)    
    dump_detail_dict_to_file(test_name, TC_FILE, TC_DICT)    

def dump_dict_to_file2(file_handler, dict):
    for key in dict:
        file_handler.write(key)
        file_handler.write(':')
        file_handler.write(str(dict[key]))
        file_handler.write('\n')

def DumpTopResult2(test_name):
    path_name = test_name
    filepath = os.path.join(path_name, TOP_RESULT_FILE)
    make_sure_path_exists(path_name)

    file_handler=open(filepath,'w+')
    file_handler.write('='*100 + '\n')    
    dump_dict_to_file2(file_handler, TOTAL_DICT)

    file_handler.write('CRASH' + '>'*100 + '\n')    
    dump_dict_to_file2(file_handler, CRASH_SPLIT_DICT)    

    file_handler.write('ANR' + '>'*100 + '\n')    
    dump_dict_to_file2(file_handler, ANR_SPLIT_DICT)    

    file_handler.write('FC' + '>'*100 + '\n')    
    dump_dict_to_file2(file_handler, FC_SPLIT_DICT)    

    file_handler.write('TC' + '>'*100 + '\n')    
    dump_dict_to_file2(file_handler, TC_SPLIT_DICT)    
    
    file_handler.close()

def get_device_info(test_name, time_stamp, package, tag, logcat_result):
    try:
        path_name = os.path.join(test_name, time_stamp+'_'+package+'_'+tag)
        #print path_name
        make_sure_path_exists(path_name)

        call_adb_pull_to_file(ANR_CMD, path_name, ANR_PATH)
        call_adb_pull_to_file(SDCARD_SEMS_CMD, path_name, SDCARD_SEMS_PATH)
        call_adb_pull_to_file(SDCARD_LOGS_CMD, path_name, SDCARD_LOGS_PATH)
        call_adb_pull_to_file(DROPBOX_CMD, path_name, DROPBOX_PATH)
        call_adb_pull_to_file(TOMBSTONES_CMD, path_name, TOMBSTONES_PATH)

        logcat_file = os.path.join(path_name, LOGCAT_FILE)
        file_handler=open(logcat_file,'w+')
        file_handler.write(logcat_result)
        file_handler.close()

    except Exception,e:
        print str(e)

def call_adb_pull_to_file(adb_shell_cmd, path, sub_path):
    path_name = os.path.join(path, sub_path)
    #print path_name
    make_sure_path_exists(path_name)
    os.system(adb_shell_cmd + ' ' + path_name)
    time.sleep(2)

def usage():  
    print '''  
    Usage: log_parser [options...]  
    Options:   
    -a : A size of logcat context
    -b : B size of logcat context
    -c : Clean output directory or not (1: yes, 0: ignore)
    -s : Parser step
    log_parser -a 5 -b 5 -c 1 -s 10000
    '''
    
try:
    opts, args = getopt.getopt(sys.argv[1:],'a:b:c:s:')
except getopt.GetoptError:
    usage()  
    sys.exit()
   
if len(opts) == 0:  
    usage()  
    sys.exit()
else:
    a_size = (-1)*(int(opts[0][1])+1)
    b_size = int(opts[1][1])
    CLEAN_TAG = int(opts[2][1])
    PARSER_STEP = int(opts[3][1])
    
# Clean if needed
if (CLEAN_TAG == 1):
    if os.path.exists(REPORTS_PATH):
        try:
            shutil.rmtree(REPORTS_PATH)
        except OSError:
            os.remove(REPORTS_PATH)

# get current timestamp
now = datetime.datetime.now()
otherStyleTime = now.strftime("%Y-%m-%d-%H-%M-%S")
test_name = REPORTS_PATH + str(otherStyleTime)
print test_name + ' is starting'

# main pipeline
#input = os.popen("cat ./logs/*.txt")
input = os.popen(ADB_FETCH_LOGS_CMD)

while True:
    try:
        line = input.readline()
        q.append(line.rstrip())
        parser_count += 1

        # 100K lines parsed and create phrased report
        if ((len(line) > 0) and (parser_count % PARSER_STEP == 0)):
            DumpTopResult2(test_name) 
            #DumpTopResult(test_name) 
            DumpDetailResult(test_name)
            sys.stdout.write("=")
            sys.stdout.flush()

        # pipe line is empty, so create final report and quit
        if (len(line) == 0):
            print '\n' + test_name + ' is ending ...'
            DumpTopResult2(test_name)
            #DumpTopResult(test_name) 
            DumpDetailResult(test_name)
            break

        # verify each tag_key for each line
        for key in TAG_DICT:
            if (line.find(TAG_DICT[key]) >= 0):
                ############################################
                ### update total result dict with tag key
                ############################################
                insert_result_to_total_dict(key)

                # package name 
                package = None
                package_found = 0
                    
                # next line to  
                line2 = ''

                ### A part
                a_list = q[a_size:-1]
                log_result = '>'*100
                log_result += '\n'
                log_result += '\n'.join(a_list)
                log_result += '\n'

                ### TAG line START
                log_result += '+'*100
                log_result += '\n'

                # TAG line
                log_result += line.rstrip()
                log_result += '\n'
                
                # parse the tag line 
                tag_list = line.rstrip().split(' ')
                for tag_item in tag_list:
                    if (tag_item.find('com.')==0):
                        if (tag_item.find('/')>0):
                            char_pos = tag_item.find('/')
                            package = tag_string[0:char_pos]
                        elif (tag_item.find(',')>0):
                            char_pos = tag_item.find(',')
                            package = tag_item[0:char_pos]
                        else:
                            package = tag_item
                        insert_result_to_split_dict(key, package)
                        package_found = 1
                        break

                #####################
                # FC is one exception
                #####################
                if ((key == 'FC') and (package_found == 0)):
                    # read the next line to find package name
                    line2 = input.readline()
                    tag_list2 = line2.rstrip().split(' ')
                    for tag_item2 in tag_list2:
                        if (tag_item2.find('com.')==0):
                            if (tag_item2.find(',')>0):
                                char_pos = tag_item2.find(',')
                                package = tag_item2[0:char_pos]
                            else:
                                package = tag_item2
                            insert_result_to_split_dict(key, package)
                            package_found == 1
                            break

                if ( (package is None) and (package_found == 0)):                
                    # default package name
                    now3= datetime.datetime.now()
                    otherStyleTime3 = now3.strftime("%H-%M-%S")
                    package = key
                    package += '_'
                    package += otherStyleTime3
                    insert_result_to_split_dict(key, package)
                                            
                #########################################################
                ### update split result dict with tag key and packagename
                #########################################################
                #insert_result_to_split_dict(key, package)
                        
                if ((key == 'FC') and (len(line2) > 0)):
                    log_result += line2.rstrip()
                    log_result += '\n'

                ### TAG line END
                log_result += '+'*100
                log_result += '\n'

                ### B part (PIPE:readline b_size times more)
                for i in range(b_size):
                    b_list.append(input.readline().rstrip())
                log_result += '\n'.join(b_list)
                log_result += '\n'
                log_result += '<'*100
                log_result += '\n'

                
                #########################################################
                ### insert detailed log info detailed dict
                #########################################################
                insert_result_to_detail_dict(key, package, log_result)

                #########################################################
                # create milisec to avoid directory overwiting
                #########################################################
                now2 = datetime.datetime.now()
                otherStyleTime2 = now2.strftime("%H-%M-%S")
                milisec = time.time() * 1000
                otherStyleTime2 += '_'
                otherStyleTime2 += str(int(milisec))

                ########################################
                # dump log file for current running case
                ########################################
                get_device_info(test_name, otherStyleTime2, package, key, log_result)

                # refresh report file 
                DumpTopResult2(test_name) 
                DumpDetailResult(test_name)
                            
                a_list=[]
                b_list=[] 

    except KeyboardInterrupt:
        print '\n' + test_name + ' Stopping... (Hit ENTER to abort, type quit to generate results and exit.)'
        response = raw_input()
        if response == 'quit':
            print 'Generating report...'
            DumpTopResult2(test_name) 
            #DumpTopResult(test_name)
            DumpDetailResult(test_name) 
            print 'Quitting...'           
            sys.stdout.flush()
            break;
        else:
            print test_name + ' Aborting...'
            sys.stdout.flush()
            break;
