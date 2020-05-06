#! /usr/bin/python3

import argparse
import datetime as dt
import glob
import os
import re
import time
import wget


# fuction to make directory
def makeDir(dirName):
    if not os.path.exists(dirName):
        os.makedirs(dirName)

def main():
    # getting inputs from command line
    parser = argparse.ArgumentParser(description='input URL and directory and also name of the file ')

    parser.add_argument('--url', nargs='*', required=True)
    parser.add_argument('--dirName', default='dirName')
    parser.add_argument('--fileName', default='fileName')
    parser.add_argument('--options', default='noChatVoice')

    args = parser.parse_args()

    # make direcory
    outputDir = args.dirName
    outputFile = args.fileName
    voiceChat = args.options
    makeDir(outputDir)

    #download zip file and extract it
    url = f'{args.url[0]}/output/{outputFile}.zip?download=zip'
    wgetCommand = f'wget -nc -O {outputFile}.zip {url}'
    os.system(wgetCommand)
    unzipCommand = f'unzip -n {outputFile}.zip -d {outputDir}'
    os.system(unzipCommand)

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
    if voiceChat == 'noChatVoice' :

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
