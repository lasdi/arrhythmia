#The data in mitbih_train.csv and mitbih_test.csv are ordered by classification
#This script randomizes the datasets and splits mitbih_train.csv into a training and validation set to be passed into the CNN
#Original data: mitbih_train.csv, mitbih_test.csv
#Destination data generated by this script: mitbih_train_random.csv, mitbih_valid_random.csv, mitbih_test_random.csv

import random

#transfers a random sample of half the data in mitbih_train.csv to mitbih_train_random.csv file
file = open("data/ordered_data/mitbih_train.csv", "r")
destination = open("data/randomized_data/mitbih_train_random.csv", "a")
total = file.readlines()
half = int(len(total) / 2)
file.close()
while len(total) > half:
    print(len(total))
    random_num = random.randint(0, len(total) - 1)
    line = total[random_num]
    destination.write(line)
    total.remove(line)
destination.close()

#transfers a random sample of the remaining half the data in mitbih_train.csv to mitbih_valid_random.csv file
destination = open("data/randomized_data/mitbih_valid_random.csv", "a")
while len(total) > 0:
    print(len(total))
    random_num = random.randint(0, len(total) - 1)
    line = total[random_num]
    destination.write(line)
    total.remove(line)
destination.close()

#transfers the data from mitbih_test.csv to mitbih_test_random.csv in a random fashion
file = open("data/ordered_data/mitbih_test.csv", "r")
destination = open("data/randomized_data/mitbih_test_random.csv", "a")
total = file.readlines()
file.close()
while len(total) > 0:
    print(len(total))
    random_num = random.randint(0, len(total) - 1)
    line = total[random_num]
    destination.write(line)
    total.remove(line)
destination.close()