# AMR will excute this "main.py" when 'Local Task Manager' is starting, its lifetime follows 'Local Task Manager'
# However, if "main.py" has no infinity loop, this program may exit earlier in normal.


# Techanically, you can write anything... just take care, DO NOT blow all system up.  
import time
import device

me = device.robot("127.0.0.1")

count = 0
while(1):
    count += 1
    print("count =", count)
    time.sleep(3.0)



