'''
Stanford Dogs Dataset Preprocessing

Modified 3/17/2020

Original dataset from: http://vision.stanford.edu/aditya86/ImageNetDogs/ (Download Images)
Preprocessing to:
* Reorganize subdirectories
* Create labels.csv containing ids and respective breed label
* Train/Test/Validation split 
'''

# Imports 
import glob
import os
import pandas as pd 
import split_folders


# Collect all breed subdirectories
files = [x[0] for x in os.walk('C:\\Users\\Allison Aprile\\Desktop\\Images\\')]

# Rename subdirectories to match Petfinder breed conventions
dir = 'C:\\Users\\Allison Aprile\\Desktop\\Images\\'
for f in files:
    last = f.rindex('\\') + 11
    name = f[last:].lower()
    os.rename(f, os.path.join(dir,name))
    
# Collect all breed subdirectories (now correct)    
subs = [y[0] for y in os.walk('C:\\Users\\Allison Aprile\\Desktop\\Images\\')][1:]

# Save id and breed into list of tuples
recs = []
for s in subs:
    dogs = glob.glob(s + '\\*.jpg')
    last_s = s.rindex('\\') + 1
    name_s = s[last_s:].lower()
    
    for d in dogs:
        last_d = d.rindex('\\') + 1
        name_d = d[last_d:-4].lower()
        recs.append((name_d, name_s))

# Create CSV containing ids and respective breed label    
df = pd.DataFrame(recs, columns =['id', 'breed']) 
df.to_csv('stanford_labels.csv', index=False)

# Train/Test/Validation split (.8, .1, .1)
split_folders.ratio('C:\\Users\\Allison Aprile\\Desktop\\images_copy', output="C:\\Users\\Allison Aprile\\Desktop\\stanford", seed=1337, ratio=(.8, .1, .1))
