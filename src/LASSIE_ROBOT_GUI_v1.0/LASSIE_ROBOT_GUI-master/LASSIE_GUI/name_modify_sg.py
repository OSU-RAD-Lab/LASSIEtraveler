# remove all the ':' and ' ' in the filenames. 
# author: Sen Gao

import os

directory = "/dropbox/Dropbox/fieldtest_manhatton_beach/traveler_log/experiment_traveler_leg/experiment_data"

print("start iterating")

# iterate over files in that directory
for filename in os.listdir(directory):
    print(directory + '/' + filename)
    name_old = directory + '/' + filename
    name_new = name_old.replace(' ', '_').replace(':','_')
    os.rename(name_old, name_new)

print("end iterating")