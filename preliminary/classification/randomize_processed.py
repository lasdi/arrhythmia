import random

file = open("data/normalized_data/all_data_normalized.csv", "r")
destination = open("data/normalized_data/all_data_normalized_randomized.csv", "a")
total = file.readlines()
file.close()
while len(total) > 0:
    print(len(total))
    random_num = random.randint(0, len(total) - 1)
    line = total[random_num]
    destination.write(line)
    total.remove(line)
destination.close()

file = open("data/normalized_data/all_data_normalized_randomized.csv", "r")
destination = open("data/normalized_data/train.csv", "a")
total = file.readlines()
half = int(len(total) * 0.6)
file.close()

while len(total) > half:
    print(len(total))
    random_num = random.randint(0, len(total) - 1)
    line = total[random_num]
    destination.write(line)
    total.remove(line)
destination.close()


half = int(len(total) * 0.6)
destination = open("data/normalized_data/valid.csv", "a")
while len(total) > half:
    print(len(total))
    random_num = random.randint(0, len(total) - 1)
    line = total[random_num]
    destination.write(line)
    total.remove(line)
destination.close()


destination = open("data/normalized_data/test.csv", "a")
while len(total) > 0:
    print(len(total))
    random_num = random.randint(0, len(total) - 1)
    line = total[random_num]
    destination.write(line)
    total.remove(line)
destination.close()
