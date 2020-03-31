import os
import shutil
import time
import datetime

print("Cron started at %s" % datetime.datetime.now())
dir = "%s/static/downloads" % os.path.dirname(os.path.abspath(__file__))

bef_timestamp = str(int(time.time()) - 86400)

for folder in os.listdir(dir):
    if folder < bef_timestamp:
        dir_path = "%s/%s" % (dir, folder)
        try:
            shutil.rmtree(dir_path)
        except OSError as e:
            print("Error: %s : %s" % (dir_path, e.strerror))

        print(dir_path)
print("------------------------------------------")
