# adobeConnectDownloader

a way to download your class recorded meeting that set up in adobe connect platform

Requirements:

* python 3

and below requirement should be install by sudo apt install PACKAGENAME

* ffmpeg
* wget
* unzip

before any this the 0.01 version and just work fine under below conditions :

  for classes that:
    1- the Host(Professor) share their own screen not slides
    2- no passwords set for the class
    
# How to run 

clone the prject and in project directory run below command :

python3 adobeDownloader.py --url='LINK_TO_SESSION' --dirName='COURSE_NAME' --fileName='SESSION'

for example :

python3 adobeDownloader.py --url='http://*/p5u78g9re5i --dirName='math' --fileName='session7'

note : make sure your link **does not** end with /

the final video is SESSION.avi(session7.avi) and you can detele other files in the folder .

# advance 

this code merge all chat voice of Participants to file and this process could take times if you dont want this voices just use False and the end of the command so the whole command is :

python3 adobeDownloader.py --url='http://*/p5u78g9re5i --dirName='math' --fileName='session7' --options='noVoiceChat'

the video output is session70.avi

# TODOS

- [ ]Deleting out file in each step in "adding all chat voice to .avi file"

- [ ]use below idea to merge all voice in one go
#https://stackoverflow.com/questions/48169031/how-to-add-audio-to-existing-video-using-ffmpeg-at-specific-time

- [ ]normilizing the output volume
#https://superuser.com/questions/323119/how-can-i-normalize-audio-using-ffmpeg

# contribute

help to imporve this code and also report any issue that you face with .

email : mohamad.shadfar54@gmail.com

have fun .
