import os

with os.scandir(r'C:StorageFiles/019b65f1-633b-749b-b638-00910c54c96e') as entries:
    for e in entries:
        print(e.name)