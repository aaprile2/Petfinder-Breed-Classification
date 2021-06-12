'''
Predict on Mixed-Breed Capable Classifier

Updated: April 22, 2020
'''

# Imports
from keras.models import load_model, Sequential
from keras.layers import Dense, Dropout
import numpy as np
from keras.applications import inception_v3
import numpy as np
from keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img
from keras.models import Sequential
from keras.layers import Dropout, Flatten, Dense
from keras import applications
from keras.applications import inception_v3
from keras.utils.np_utils import to_categorical
from keras.preprocessing import image
from PIL import Image
from glob import glob

#####################
# RECONSTRUCT MODEL #
#####################

# Define model architecture
model = Sequential()
model.add(Dense(256, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(120, activation='sigmoid'))

# Build and load weights
model.build(input_shape=(1, 2048))
model.load_weights('C:/Users/Allison Aprile/Documents/Temple/Spring 2020/Capstone/mixed_breed.h5')

# Compile model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
#model.summary()


###############
# PREDICTIONS #
###############

# Get breeds list
breeds = []
with open('breeds.txt', 'r+') as f:
	for line in f:
		breeds.append(line)

# Define Inception model for feature extraction
inception_bottleneck = inception_v3.InceptionV3(weights='imagenet', include_top=False, pooling='avg')

# Define testing image directory (or files)
images = glob('C:/Users/Allison Aprile/Downloads/IMG_*.jpg')

# Make and print prediction
print('PREDICTIONS:')
print('______________')
for path in images:
    img = image.load_img(path, target_size=(224, 224))

    # Create tensor for input
    x = np.expand_dims(image.img_to_array(img), axis=0).astype('float32')/255
    features = inception_bottleneck.predict(x)

    # Get top two predictions
    probs = model.predict(features)
    pred = np.argsort(model.predict(features)[0])[:-3:-1]

    # Print breeds
    print('Image: ' + path)

    # Guess if mixed or purebred
    if probs[0][pred[0]] > .9:
        print('Likely purebred')
    else:
        print('Likely mixed')

    for i in range(2):
        print("{}".format(breeds[pred[i]]) + "({:.3})".format(probs[0][pred[i]]))

    print("______________")


