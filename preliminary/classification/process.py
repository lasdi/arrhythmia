class1_file = open("normalizedMITData/newFData.csv", "r")
class1_lines = class1_file.readlines()

destination = open("data/normalized_data/all_data_normalized.csv", "a")

for i in range(len(class1_lines)):
    curr_line_array = class1_lines[i].split(",")
    count = 0
    for j in range(len(curr_line_array)):
        if curr_line_array[j] == '0' or curr_line_array[j] == '0.0':
            count+=1
    if count == 186:
        continue
    add = class1_lines[i].strip()
    add += ",0\n"
    print(str(i) + ": Step 1")
    destination.write(add)

class1_file.close()

class1_file = open("normalizedMITData/newNData.csv", "r")
class1_lines = class1_file.readlines()


for i in range(len(class1_lines)):
    curr_line_array = class1_lines[i].split(",")
    count = 0
    for j in range(len(curr_line_array)):
        if curr_line_array[j] == '0' or curr_line_array[j] == '0.0':
            count+=1
    if count == 186:
        continue
    class1_lines[i] = class1_lines[i].strip()
    class1_lines[i] += ",1\n"
    print(str(i) + ": Step 2")
    destination.write(class1_lines[i])

class1_file.close()

class1_file = open("normalizedMITData/newQData.csv", "r")
class1_lines = class1_file.readlines()


for i in range(len(class1_lines)):
    curr_line_array = class1_lines[i].split(",")
    count = 0
    for j in range(len(curr_line_array)):
        if curr_line_array[j] == '0' or curr_line_array[j] == '0.0':
            count+=1
    if count == 186:
        continue
    class1_lines[i] = class1_lines[i].strip()
    class1_lines[i] += ",2\n"
    print(str(i) + ": Step 3")
    destination.write(class1_lines[i])

class1_file.close()

class1_file = open("normalizedMITData/newSData.csv", "r")
class1_lines = class1_file.readlines()


for i in range(len(class1_lines)):
    curr_line_array = class1_lines[i].split(",")
    count = 0
    for j in range(len(curr_line_array)):
        if curr_line_array[j] == '0' or curr_line_array[j] == '0.0':
            count+=1
    if count == 186:
        continue
    class1_lines[i] = class1_lines[i].strip()
    class1_lines[i] += ",3\n"
    print(str(i) + ": Step 4")
    destination.write(class1_lines[i])

class1_file.close()

class1_file = open("normalizedMITData/newVData.csv", "r")
class1_lines = class1_file.readlines()


for i in range(len(class1_lines)):
    curr_line_array = class1_lines[i].split(",")
    count = 0
    for j in range(len(curr_line_array)):
        if curr_line_array[j] == '0' or curr_line_array[j] == '0.0':
            count+=1
    if count == 186:
        continue
    class1_lines[i] = class1_lines[i].strip()
    class1_lines[i] += ",4\n"
    print(str(i) + ": Step 5")
    destination.write(class1_lines[i])

class1_file.close()