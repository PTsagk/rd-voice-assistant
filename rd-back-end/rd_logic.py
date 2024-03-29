import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer

import tensorflow as tf
keras=tf.keras

lemmatizer=WordNetLemmatizer()

intents=json.loads(open('intents.json').read())

words=[]
classes=[]
documents=[]
igone_letters=['?','!','.',',']

for intent in intents['intents']:
    for pattern in intent['patterns']:
        word_list=nltk.word_tokenize(pattern) #split the inputs (array) in words
        words.extend(word_list)
        documents.append((word_list,intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])


words=[lemmatizer.lemmatize(word) for word in words if word not in igone_letters] #lemmatize words in array
words=sorted(set(words)) #remove duplicates
classes=sorted(set(classes))

pickle.dump(words,open('words.pkl','wb')) # wb = writing binary
pickle.dump(classes,open('classes.pkl','wb'))

training=[]
output_empty=[0]*len(classes) # creates an arry of n zeros

for document in documents:
    bag=[]
    word_patterns=document[0]
    word_patterns=[lemmatizer.lemmatize(word.lower()) for word in word_patterns]
    for word in words:
        bag.append(1) if word in word_patterns else bag.append(0) # array where there is 1 in the position of the word that is used and 0 elsewhere
    
    output_row=list(output_empty)
    output_row[classes.index(document[1])]=1 # Mark the class of the words where are 1 in the bag array
    training.append([bag,output_row])
        

random.shuffle(training)
training=np.array(training)

train_x=list(training[:,0])
train_y=list(training[:,1])

model=tf.keras.Sequential()
model.add(tf.keras.layers.Dense(128,activation='relu'))
model.add(tf.keras.layers.Dropout(0.5))
model.add(tf.keras.layers.Dense(64,activation='relu'))
model.add(tf.keras.layers.Dropout(0.5))
model.add(tf.keras.layers.Dense(len(train_y[0]),activation='softmax'))

sgd=tf.keras.optimizers.SGD(learning_rate=0.01,weight_decay=1e-6,momentum=0.9,nesterov=True)
model.compile(loss='categorical_crossentropy',optimizer=sgd,metrics=['accuracy'])

hist=model.fit(np.array(train_x),np.array(train_y),epochs=200,batch_size=5,verbose=1)
model.save('chatbotmodel.h5',hist)
print('Done')