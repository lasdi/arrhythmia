import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder

#processing training data (.csv file) by reading and labeling columns
column_names = []
for i in range(0, 186):
    column_names.append("data" + str(i))
column_names.append("label")
ecg_train = pd.read_csv("data/normalized_data/train.csv", names = column_names)

#representing training features and labels as numpy arrays
ecg_train.head()
ecg_features = ecg_train.copy()
ecg_labels = ecg_features.pop("label")
ecg_features = np.array(ecg_features)
ecg_labels = np.array(ecg_labels)

lb = LabelEncoder()
ecg_labels = lb.fit_transform(ecg_labels)

#processing validation data (.csv file) by reading and labeling columns
column_names = []
for i in range(0, 186):
    column_names.append("data" + str(i))
column_names.append("label")
valid_train = pd.read_csv("data/normalized_data/valid.csv", names = column_names)

#representing validation features and labels as numpy arrays
valid_train.head()
valid_features = valid_train.copy()
valid_labels = valid_features.pop("label")
valid_features = np.array(valid_features)
valid_labels = np.array(valid_labels)

lb = LabelEncoder()
valid_labels = lb.fit_transform(valid_labels)

ecg_features = np.reshape(ecg_features,(42592, 186, 1))
valid_features = np.reshape(valid_features,(25555, 186, 1))

#defining layers of model
ecg_model = tf.keras.Sequential([
    tf.keras.layers.Conv1D(filters=50, kernel_size=35, strides=1, activation = "relu", padding="same", input_shape=(186, 1)),
    tf.keras.layers.MaxPooling1D(pool_size=2),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(300, activation="relu"),
    tf.keras.layers.Dense(150, activation="relu"),
    tf.keras.layers.Dense(units=5, activation="softmax")
])

#compiling model and fitting features with labels by passing in training and validation data
ecg_model.compile(loss=tf.keras.losses.SparseCategoricalCrossentropy(),
                  optimizer=tf.keras.optimizers.Adam(),
                  metrics=["accuracy"])
ecg_model.fit(ecg_features, ecg_labels, epochs = 10, validation_data=(valid_features, valid_labels))

#processing test data (.csv file) by reading and labeling columns
column_names = []
for i in range(0, 186):
    column_names.append("data" + str(i))
column_names.append("label")
test_train = pd.read_csv("data/normalized_data/test.csv", names = column_names)

#representing test features and labels as numpy arrays
test_train.head()
test_features = test_train.copy()
test_labels = test_features.pop("label")
test_features = np.array(test_features)
test_labels = np.array(test_labels)

lb = LabelEncoder()
test_labels = lb.fit_transform(test_labels)

#making predictions by passing test features input into model
predictions = ecg_model.predict(test_features)

#extracting the diagnosis from the prediction matrix for each test feature and comparing with true value
pred_array = []
for i in range(len(predictions)):
    pred_array.append(np.argmax(predictions[i]))
pred_compare = []
for i in range(len(test_labels)):
    pred_compare.append(test_labels[i])
# print("True Values: " + str(pred_compare))
# print("Predictions: " + str(pred_array))

#accuracy = correctPredictions / totalPredictions
totalPredictions = 0
correctPredictions = 0
for i in range(len(pred_array)):
    totalPredictions += 1
    if (pred_array[i] == pred_compare[i]):
        correctPredictions+=1
print("Accuracy: " + str(correctPredictions / totalPredictions))
print(str(correctPredictions) + " ECG recordings correctly diagnosed out of " + str(totalPredictions) + " total inputs.")
