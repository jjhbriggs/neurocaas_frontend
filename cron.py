import os
import shutil
import time


dir = "static/downloads"
bef_timestamp = str(int(time.time()) - 86400)

for folder in os.listdir(dir):
    if folder < bef_timestamp:
        dir_path = "%s/%s" % (dir, folder)
        try:
            shutil.rmtree(dir_path)
        except OSError as e:
            print("Error: %s : %s" % (dir_path, e.strerror))

        print(dir_path)
