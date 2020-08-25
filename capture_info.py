# This program is responsible for maintaining the metadata text file for all of the radio captures. Upon user request,
# this program also returns the metadata for the requested file.
#
# Sam Miller
# 8/21/2020

from os import listdir
from os.path import isfile, join
import process_fm as px

global BLACKLIST
BLACKLIST = ["metadata.txt"]

#stores all of the pertinent info for the capture files
class File:
    def __init__(self,entry):
        File.name = entry[0]
        File.sample_rate = int(entry[1])
        File.sample_period = int(entry[2])
        File.gain = int(entry[3])


#if you delete a capture from the directory, this function will update the metadata with the file(s) removed.
def remove_entry(database,myfiles):
    num_entries = len(database)
    num_files = len(myfiles)
    db = []
    metadata = open(px.CAPTURE_PATH + "metadata.txt","w")
    metadata.write(str(num_files)+"\n")
    metadata.write("filename,sample_rate(Hz),sample_period(s),gain(dB)\n")
    for i in range(0,num_entries):
        if(database[i][0] in myfiles):
            db.append(database[i])
            entry = ",".join(database[i])
            metadata.write(entry)
    metadata.close()
    return db

#if you add a capture to the directory, this function will prompt the user to enter the metadata for the new file(s)
def add_entry(myfiles,database):
    metadata = open(px.CAPTURE_PATH + "metadata.txt","w")
    numentries = len(database)
    metadata.write(str(len(myfiles))+"\n")
    metadata.write("filename,sample_rate(Hz),sample_period(s),gain(dB)\n")
    for filename in myfiles:
        flag = -1
        for i in range(0,numentries):
            if(filename ==  database[i][0]):
                flag = 1
                metadataentry = ",".join(database[i])
                metadata.write(metadataentry)
                break
        if(flag == -1):
            sample_rate=input("What is the sample rate of {} in Hz:".format(filename))
            sample_period = input("What is the sample period of {} in s:".format(filename))
            gain = input("What is the gain of {} in dB".format(filename))
            dbentry = [filename,sample_rate,sample_period,gain]
            database.append(dbentry)
            metadataentry = ",".join(dbentry)
            metadata.write(metadataentry)

    metadata.close()
    return database

#checks the metadata file to make sure everything is up to date.
def update_metadata():
    change = False #do we need to update the metadata file?

    metadata = open(px.CAPTURE_PATH+"metadata.txt","r")
    try:
        num_files = int(metadata.readline())
        metadata.readline() #metatext
    except:
        num_files = 0
    myfiles = [f for f in listdir(px.CAPTURE_PATH) if isfile(join(".", f))]
    print(px.CAPTURE_PATH)
    print(myfiles)
    for blacklisted in BLACKLIST:
        myfiles.remove(blacklisted)
    num_captures = len(myfiles)
    if(num_files > num_captures):
        change = True
        num_files = num_captures
        
    database = []
    for i in range(0,num_files):
        fileinfo = metadata.readline()
        fileinfo = fileinfo.split(',')
        database.append(fileinfo)
    metadata.close()

    if(num_files < len(myfiles)):
        database = add_entry(myfiles,database)
    if(change):
        database = remove_entry(database,myfiles)
    return database

#returns the metadata of the specified file
def fetch(filename):
    database = update_metadata()
    num_entries = len(database)
    entry = -1
    for i in range(0,num_entries):
        if(database[i][0] == filename):
            entry = i
            break
    MyFile = File(database[entry])
    return MyFile

if __name__=="__main__":
    print(px.CAPTURE_PATH)
    update_metadata()
