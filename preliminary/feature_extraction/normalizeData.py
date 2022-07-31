import numpy as np
import csv


# Load all data from the 5 CSV files created by running extract_features() from preprocessing.py into one consolidated
# 2d array (still organized by rows with fixed data points), but exclude the filler rows that only contain 0.0. Need
# to get all data points into one 2d array so that we can calculate the minimum data point and maximum data point across
# all the files so all data can be normalized within the range of 0 to 1 (run this file after running preprocessing.py)
def load_all_data():
    consolidatedData = []

    # Two example arrays of the variations in which a row that is full of only 0 values can show up after being read
    # from the CSV files. This is so we know to ignore these rows when reading the CSV files, so they don't get added
    # to the consolidatedData[], since they're not actual data points.
    row_ex = ['0.0'] * 187
    row_ex_2 = ['0'] * 187

    # Open Ndata.csv to get all the data classified as non-ectopic beats. For each row from the CSV file, as long as
    # the row does not match either of the two examples of rows filled with all 0 values, add the row to the
    # consolidatedData.
    with open("mitData/Ndata.csv", 'r') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            if row != row_ex and row != row_ex_2:
                consolidatedData.append(row)

    # Same with Sdata.csv
    with open("mitData/Sdata.csv", 'r') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            if row != row_ex and row != row_ex_2:
                consolidatedData.append(row)

    # Same with Vdata.csv
    with open("mitData/Vdata.csv", 'r') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            if row != row_ex and row != row_ex_2:
                consolidatedData.append(row)

    # Same with Fdata.csv
    with open("mitData/Fdata.csv", 'r') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            if row != row_ex and row != row_ex_2:
                consolidatedData.append(row)

    # Same with Qdata.csv
    with open("mitData/Qdata.csv", 'r') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            if row != row_ex and row != row_ex_2:
                consolidatedData.append(row)

    # Note: data from oops.csv was not added to consolidatedData since it will be ignored

    # Since we read the values back in from CSV files, all the items in consolidatedData[] is currently in string
    # format. For each row, convert the string to a double, then add it back into a new 2d array, consolidatedNums[].
    consolidatedNums = []
    for row in consolidatedData:
        dec = []
        for num in row:
            if num != '':
                new_num = float(num)
                dec.append(new_num)
        consolidatedNums.append(dec)

    # Printing various rows to make sure that rows with all 0 values are being ignored
    print("Row 1: ", len(consolidatedData[0]), " ---> ", consolidatedData[0])
    print("Row 9: ", len(consolidatedData[8]), " ---> ", consolidatedData[8])

    print("Strings ", len(consolidatedData), " ---> ", consolidatedData[len(consolidatedData) - 1])
    print("Nums ", len(consolidatedNums), " ---> ", consolidatedNums[len(consolidatedNums) - 1])

    return consolidatedNums


if __name__ == '__main__':

    # Store entire dataset of all consolidated datapoints with load_all_data()
    all_data = load_all_data()
    min_num = 100
    max_num = -100

    # For each row in all_data, find the minimum data point in the row and the maximum data point in the row. If this
    # min is less than what was previously set as the min_num, set min_num to the new minimum. Same with max. Loop
    # through entirety of consolidated data in order to find the overall min and max for all data points.
    for signal in all_data:
        find_min = np.min(signal)
        find_max = np.max(signal)

        if find_min < min_num:
            min_num = find_min

        if find_max > max_num:
            max_num = find_max

    print("Min: ", min_num)
    print("Max: ", max_num)

    # Process is for 1 CSV file: Open the old CSV file for one of the AAMI classes (with data that has been filtered
    # and sorted but not yet normalized). For each row in the old CSV file, first convert each number from a string
    # to a decimal. Then, if the number is anything other than 0.0 (want to keep all the 0s for padding), add the
    # normalized value of that number to the normalizedNums[] array (calculated using the overall min and max that
    # we previously got from the dataset). Once all the numbers in a row are normalized, add that array to a new
    # 2d array of normalizedRows[] in order to normalize all the numbers in all the rows of the old CSV.
    with open("mitData/Vdata.csv", 'r') as file:
        csvreader = csv.reader(file)
        normalizedRows = []
        for row in csvreader:
            normalizedNums = []
            for num in row:
                if num != '':
                    new_num = float(num)
                    if new_num != 0.0:
                        normalizedNums.append((new_num - min_num) / (max_num - min_num))
                    else:
                        normalizedNums.append(0.0)
            normalizedRows.append(normalizedNums)

    # Create a new file that will be the exact same format as the old CSV file for that AAMI class (107,873 rows with
    # fixed number of data points, should have same number of rows with all 0.0s at the same row numbers), but will
    # contain all the normalized values (none of the 0.0 values were normalized). Write each of the rows in the
    # normalizedRow[] 2d array to the new CSV file.
    # REPEAT THIS PROCESS FOR ALL 5 CSV FILES!!!
    file_name = 'newVData.csv'
    with open(file_name, 'a',  newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')

        csv_writer.writerows(normalizedRows)
