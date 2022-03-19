import sys

from lib import settings
from lib.functions import console

modulname = "Timelapse"
import os
import numpy as np
import cv2
import time
import datetime
sys.path.insert(0, "/lib/")
sys.path.insert(0, "/settings/")
from utils import CFEVideoConf, image_resize
import glob
cap = cv2.VideoCapture(0)


fps=settings.fps
timelapse_total_time =settings.timelapse_total_time
timelapse_pic_interval=settings.timelapse_pic_interval
timelaps_folder_picture=settings.timelaps_folder_picture
timelaps_folder_video=settings.timelaps_folder_video

console(modulname,"Timelapse Einstelungen wurden geladen")
console(modulname,"FPS:"+str(fps))
console(modulname,"Videolänge der Timelapse:"+str(timelapse_total_time ))
console(modulname,"1 Foto wird alle :"+str(timelapse_pic_interval)+"Sekunden geschossen")
console(modulname,"Bild-pfad: "+timelaps_folder_picture)
console(modulname,"Video-Pfad: "+timelaps_folder_video)
frames_per_seconds = fps
save_path=timelaps_folder_video+"/timelapse"+str(time.strftime("%d_%m_%y",time.localtime()))+'.mkv'
config = CFEVideoConf(cap, filepath=save_path)
out = cv2.VideoWriter(save_path, config.video_type, frames_per_seconds, config.dims)
timelapse_img_dir = timelaps_folder_picture
seconds_duration = ((timelapse_total_time*60)*60)
seconds_between_shots =timelapse_pic_interval*60

if not os.path.exists(timelapse_img_dir):
    os.mkdir(timelapse_img_dir)

now = datetime.datetime.now()
finish_time = now + datetime.timedelta(seconds=seconds_duration)
current_time = str(time.strftime('%H-%M-%S', time.localtime()))

i = 0
while datetime.datetime.now() < finish_time:
    '''
    Ensure that the current time is still less
    than the preset finish time
    '''
    ret, frame      = cap.read()
    filename        = f"{timelapse_img_dir}/{i}-{current_time}.jpg"
    i               += 1
    cv2.imwrite(filename, frame)
    console(modulname,"Aufname wurde gespeichert:"+filename)
    time.sleep(seconds_between_shots)
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break


def images_to_video(out, image_dir, clear_images=True):
    image_list = glob.glob(f"{image_dir}/*.jpg")
    sorted_images = sorted(image_list, key=os.path.getmtime)
    for file in sorted_images:
        image_frame  = cv2.imread(file)
        out.write(image_frame)
    if clear_images:
        '''
        Remove stored timelapse images
        '''
        for file in image_list:
            os.remove(file)


images_to_video(out, timelapse_img_dir)
console(modulname,"Timelapse wurde erstellt -"+save_path)
# When everything done, release the capture
cap.release()
out.release()
cv2.destroyAllWindows()
from subprocess import Popen
console(modulname,"Neue Timelapse wird gestartet ....")
Popen("timelaps.py", shell=True) # start reloader