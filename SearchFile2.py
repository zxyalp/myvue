import os
#
rootdir = "F:\\work\\workspace\\workspace1.1\\file\\IT\\项目级\\TMS-周迭代\\3.0.31\\"
query = "SETTLE_DT"

def walk_all_files(rootdir ,query):
    print(os.walk(rootdir))
    for parent,dirnames,filenames in os.walk(rootdir):
        # for dirname in dirnames:
        #     print("parent is :"+parent)
        #     print("dirname is:"+dirname)
        #     pass
        ##print(filenames)
        for filename in filenames:
            #print("fileName:"+filename)
            is_file_contain_word(os.path.join(parent,filename),query)

def is_file_contain_word(file_,query_word):
    #print("search file:" + file_)
    file_suffix = os.path.splitext(file_)[1]
    if file_suffix != '.sql':
        #print("file_suffix:"+file_suffix)
        return

    if query_word in open(file_,encoding='UTF-8').read():
        print (file_)
        filecontext = open(file_,encoding='UTF-8').read()
        lines = filecontext.split('\n')
        for line in lines:
            if query_word in line:
                print(line)

walk_all_files(rootdir,query.upper())

print("done")