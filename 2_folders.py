import os
import shutil
import sys
import logging
import time
from watchdog.events import LoggingEventHandler
from watchdog.observers import Observer


def main():
    try:
        print("Begin sync")
        checkIfRootDirsExist(srcDir, dstDir)
        syncDirs(srcDir, dstDir)
        syncFiles(srcDir, dstDir)
        print("End sync with success")
    except Exception as e:
        print(e)
        print("End sync with failure!")


def checkIfRootDirsExist(rootDir1, rootDir2) :
    if (not os.path.exists(rootDir1) and not os.path.isdir(rootDir1)) :
        raise Exception(rootDir1 + " doesn't exist")
    if (not os.path.exists(rootDir2) and not os.path.isdir(rootDir2)) :
        raise Exception(rootDir2 + " doesn't exist")


def syncDirs(rootDir1, rootDir2):
    for root1, dirs1, files1 in os.walk(rootDir1):
        for relativePath1 in dirs1 :
            fullPath1 = os.path.join(root1, relativePath1)
            fullPath2 = fullPath1.replace(rootDir1, rootDir2)
            if os.path.exists(fullPath2) and os.path.isdir(fullPath2) :
                continue
            if os.path.exists(fullPath2) and os.path.isfile(fullPath2) :
                raise Exception("Cannot perform dir sync." + str(fullPath2) + " should be a dir, not a file!")
            # Case 1 : dest dir does not exit
            shutil.copytree(fullPath1, fullPath2)
            print("Directory " + str(fullPath2) + " copied from " + str(fullPath1))
            continue



def syncFiles(rootDir1, rootDir2):
    for root1, dirs1, files1 in os.walk(rootDir1):
        for file1 in files1:
            fullPath1 = os.path.join(root1, file1)
            fullPath2 = fullPath1.replace(rootDir1, rootDir2)
            if (not os.path.exists(fullPath2)) :
                shutil.copy2(fullPath1, fullPath2)
                print("File " + str(fullPath2) + " copied from " + str(fullPath1))
                continue
            file1LastModificationTime = round(os.path.getmtime(fullPath1))
            file2LastModificationTime = round(os.path.getmtime(fullPath2))
            if (file1LastModificationTime > file2LastModificationTime):
                os.remove(fullPath2)
                shutil.copy2(fullPath1, fullPath2)
                print("File " + str(fullPath2) + " synchronized from " + str(fullPath1))
                continue
            if (file1LastModificationTime < file2LastModificationTime):
                os.remove(fullPath1)
                shutil.copy2(fullPath2, fullPath1)
                print("File " + str(fullPath1) + " synchronized from " + str(fullPath2))
                continue



def monitor(logDir,timeToRecover):
    #Add basic config
    file_log = logging.FileHandler(logDir)
    console_out = logging.StreamHandler()
    logging.basicConfig(handlers=(file_log, console_out),
                        format='[%(asctime)s | %(levelname)s]: %(message)s',
                        datefmt='%m.%d.%Y %H:%M:%S',
                        level=logging.INFO)

    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    e_handler = LoggingEventHandler()
    watch = Observer()
    watch.schedule(e_handler, path, recursive=True)
    watch.start()


if __name__ == '__main__':
    srcDir = str(input('enter folder 1 in format E:/program/program:'))
    dstDir = str(input('enter folder 2 in format E:/program/program:'))
    logDir = str(input('enter folder for log in format E:/program/program:'))
    timeToRecover = int(input('time to recovery:'))

    try:
        while True:
            main()
            monitor(logDir, timeToRecover)
            time.sleep(timeToRecover)
    except KeyboardInterrupt:
        main.stop()
    main.join()