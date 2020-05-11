#! /usr/bin/python3

import argparse
import datetime as dt
import glob
import os
import re
import platform
import requests
import zipfile
import sys

# fuction to make directory
def makeDir(dirName):
    if not os.path.exists(dirName):
        os.makedirs(dirName)

# function to download zip file         
def downloadZipFile(url, dirPath, chunk_size=4096):
    response = requests.get(url, stream=True)
    print("Downloading zip file ... ")
    with open(dirPath, 'wb') as f:
        totalLength = response.headers.get('content-length')
        if totalLength is None: 
            f.write(response.content)
        else:
            dl = 0
            totalLength = int(totalLength)
            for data in response.iter_content(chunk_size=chunk_size):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / totalLength)
                sys.stdout.write("\r progress bar : [%s%s] %d%%" % ('=' * done, ' ' * (50-done),int((dl/totalLength)*100)) )    
                sys.stdout.flush()

# get operating system
platform = platform.system().lower()
print('your platform is : ', platform)

#check for operating system
if platform == 'linux' or platform == 'linux2':
    platform = 'linux'
elif platform == 'darwin':
    platform = 'darwin'
elif platform == 'win32':
    platform = 'windows'   

def main():
    # getting inputs from command line
    parser = argparse.ArgumentParser(description='input URL and directory and also name of the file ')

    parser.add_argument('--url', default='', nargs='*')  # , required=True)
    parser.add_argument('--dirName', default='dirName')
    parser.add_argument('--fileName', default='fileName')
    parser.add_argument('--options', default='ChatVoice')
    parser.add_argument('--fileExist', default=False,action='store_true')

    args = parser.parse_args()

    # saving args
    url = args.url
    outputDir = args.dirName
    outputFile = args.fileName
    voiceChat = args.options

    #get current Dir path
    dirPath = os.getcwd()
    if platform == 'linux' or platform == 'darwin' :
        dirPath = dirPath+f'/{outputFile}.zip'
        url = url[0]
    elif platform == 'windows':
        url = url[0][1:-1]
        outputDir = outputDir[1:-1]
        outputFile = outputFile[1:-1]
        dirPath = dirPath+f'\{outputFile}.zip'
        
    # make direcory
    makeDir(outputDir)
       
    #print(url,outputDir,outputFile,dirPath)
    #download zip file  
    if(not args.fileExist):
        if(url == ""):
            print("No Url has specified, Give me one using --url ""url"" ")
            exit()
        else:
            sessioncode = url
            if (sessioncode[-1] == '/'):
                sessioncode = sessioncode[0:-1]
                    
            url = sessioncode + f'/output/{outputFile}.zip?download=zip'
            
            if os.path.exists(f'{outputFile}.zip'):
                os.remove(f'{outputFile}.zip')
            else:
                print("The file does not exist and will be downloaded")
            #print(url)
            downloadZipFile(url, dirPath, chunk_size=4096)

    # unzip zip file
    with zipfile.ZipFile(f'{outputFile}.zip', 'r') as zipRef:
        zipRef.extractall(f'{outputDir}')

    #get ready to add *.flv together
    cameraVoipFilePaths = {"path":[],"time":[]}
    for cvfilepaths in sorted(glob.glob(os.path.join(outputDir, 'cameraVoip_*.flv'))):
        cameraVoipFilePaths["path"].append(cvfilepaths)  

    xmlCameraVoipFilePaths = []
    for xcvfilepaths in sorted(glob.glob(os.path.join(outputDir, 'cameraVoip_*.xml'))):
        xmlCameraVoipFilePaths.append(xcvfilepaths)

    for i in range(len(xmlCameraVoipFilePaths)):
            f=open(f'{xmlCameraVoipFilePaths[i]}','r')
            lines=f.readlines()
            pattern = re.compile(r":")
            for line in lines:
                if pattern.search(line) != None: 
                    cameraVoipFilePaths["time"].append(line[40:48])

    start=cameraVoipFilePaths["time"][0]
    for i in range(1,len(cameraVoipFilePaths["time"])):
        end=cameraVoipFilePaths["time"][i]
        start_dt = dt.datetime.strptime(start, '%H:%M:%S')
        end_dt = dt.datetime.strptime(end, '%H:%M:%S')
        diff = (end_dt - start_dt) 
        cameraVoipFilePaths["time"][i] = int(diff.seconds )*1000
    cameraVoipFilePaths["time"][0] = 0 
    print(cameraVoipFilePaths) 

    screenshareFilepaths = []
    for filepaths in sorted(glob.glob(os.path.join(outputDir, 'screenshare_*.flv'))):
        screenshareFilepaths.append(filepaths)
    print(screenshareFilepaths)

    # merge audio and video file and convert it to avi format
    i = 0
    for cameraVoipFilePath, screenshareFilepath in zip(cameraVoipFilePaths["path"], screenshareFilepaths):
        mergeCommand = f'ffmpeg -i {cameraVoipFilePath} -i {screenshareFilepath} -c copy -map 0:a:0 -map 1:v:0 -shortest -y {outputFile}{i}.flv'
        
        os.system(mergeCommand)
        aviConversionCommand = f'ffmpeg -i {outputFile}{i}.flv -f avi -vcodec mpeg4 -acodec libmp3lame {outputFile}{i}.avi'
        
        os.system(aviConversionCommand)
        i += 1
    
    #adding all chat voice to .avi file 
    if voiceChat == 'ChatVoice' :
        print("adding all chat voice to .avi file ")
        last_succes_i = 0
        for i in range(len(cameraVoipFilePaths["path"])-1):

            if os.path.isfile(f'{outputFile}{i}.avi'):
                
                addCommand = f'ffmpeg -i {outputFile}{i}.avi -i {cameraVoipFilePaths["path"][i+1]} -filter_complex "[1]adelay={cameraVoipFilePaths["time"][i+1]}[aud];[0][aud]amix" -c:v copy {outputFile}{i+1}.avi'
                os.system(addCommand)
                last_succes_i = i
            else:
                
                addCommand = f'ffmpeg -i {outputFile}{last_succes_i}.avi -i {cameraVoipFilePaths["path"][i+1]} -filter_complex "[1]adelay={cameraVoipFilePaths["time"][i+1]}[aud];[0][aud]amix" -c:v copy {outputFile}{i+1}.avi'
                os.system(addCommand)
                if os.path.isfile(f'{outputFile}{i}.avi'):
                    last_succes_i = i

        # add the main voice to the file cause the volume decrese in some parts of the file for adding voice chat to it      
        boostCommand = f'ffmpeg -i {outputFile}{last_succes_i}.avi -i {cameraVoipFilePaths["path"][0]} -filter_complex "[1]adelay=0[aud];[0][aud]amix" -c:v copy {outputFile}.avi'
        os.system(boostCommand)

if __name__ == "__main__":
    main()


#TODO
#deleting out file in each step in "adding all chat voice to .avi file"

#TODO use below idea to merge all voice in one go
#https://stackoverflow.com/questions/48169031/how-to-add-audio-to-existing-video-using-ffmpeg-at-specific-time

#TODO normilizing the output volume
# https://superuser.com/questions/323119/how-can-i-normalize-audio-using-ffmpeg
