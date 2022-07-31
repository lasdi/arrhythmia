from modwt import modwt
from modwt import imodwt
from numpy import shape
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import wfdb
from scipy.signal import find_peaks
from wfdb import processing
import csv
import os


# Uses maximal overlap discrete wavelet transform to filter raw ECG signal and save filtered signal data to CSV file
def get_filtered_signal(record):

    # Parameters: record = name of file that you want to process (ex: 'mitdb/100')
    # sample_end = sample number to stop processing ECG signal at (can just delete this to process entire file)

    # Sig is a numpy array that stores raw ECG signal after reading in .dat file (only reads in first channel? ML11?)
    sig, fields = wfdb.rdsamp(record, channels=[0])

    # Use modwt() function to perform maximal overlap discrete wavelet transform on raw ECG signal
    # uses Symlet wavelets with 4 vanishing points (recommended for ECG signal) with 6 different scales (test which one
    # is ideal)
    wt = modwt(sig, 'sym4', 6)

    # Array to store coefficients that correspond to scale 2^3 for modwt (test different scales by plotting wavelets
    # from modwt to see which one gets rid of noise best)
    # For us, 3 or 4 seems best
    reconstruct = np.zeros(shape(wt))
    reconstruct[3, :] = wt[3, :]

    # Use inverse function to create reconstructed ECG signal with data from scale 2^3
    reconstructed_ECG = imodwt(reconstruct, 'sym4')


    # Store reconstructed ECG signal in CSV file
    # Square reconstructed ECG signal to get rid of negative numbers (not sure if this is actually needed / if it
    # messes up the data)
    new_data = pd.DataFrame(reconstructed_ECG ** 2)
    new_data.to_csv(record[6:9] + 'filtered.csv')


# Creates three plots: 1) the original ECG signal, 2) the reconstructed ECG signal, 3) reconstructed ECG signal with
# detected QRS complexes labeled
def plot_all_signals(record, sample_start, sample_end):

    # Parameters: record = name of file to process, sample_end = sample number to stop processing ECG signal at (process
    # portion to make graph more readable instead of whole ECG signal)

    # Sig is a numpy array that stores raw ECG signal after reading in .dat file (only reads in first channel? ML11?)
    sig, fields = wfdb.rdsamp(record, sampfrom=sample_start, sampto=sample_end, channels=[0])

    # Use modwt() function to perform maximal overlap discrete wavelet transform on raw ECG signal
    # uses Symlet wavelets with 4 vanishing points (recommended for ECG signal) with 6 different scales (test which one
    # is ideal)
    wt = modwt(sig, 'sym4', 6)

    # Use matplotlib to create figure window to display the three ECG plots
    plt.rcParams["figure.figsize"] = [14.0, 7.0]
    plt.rcParams["figure.autolayout"] = True

    # Evenly spaced numbers over interval from 0 to the last sample number processed from the ECG file (ex: 0 to 3000)
    # What we will use for the interval of the x-axis of our plots to mimic sample numbers from the ECG
    x = np.linspace(sample_start, sample_end, sample_end - sample_start)

    # Create 3 subplots within our figure (for the 3 graphs)
    fig, axs = plt.subplots(3)

    # FIRST GRAPH: even interval of sample numbers on x-axis, raw ECG signal on y-axis
    # plots the original, un-filtered ECG signal from the raw MIT-BIH files
    axs[0].plot(x, sig, color='red')

    # Array to store coefficients that correspond to scale 2^3 for modwt (test different scales by plotting wavelets
    # from modwt to see which one gets rid of noise best)
    # For us, 3 or 4 seems best
    reconstruct = np.zeros(shape(wt))
    reconstruct[3, :] = wt[3, :]

    # Use inverse function to create reconstructed ECG signal with data from scale 2^3
    reconstructed_ECG = imodwt(reconstruct, 'sym4')

    # SECOND GRAPH: even interval of sample numbers on x-axis, filtered ECG signal on y-axis
    # plots the new, filtered ECG signal after discrete wavelet transform was performed and signal was reconstructed
    axs[1].plot(x, reconstructed_ECG, color='blue')

    # Use find_peaks to detect the QRS complexes in the filtered ECG signal with the condition for a QRS complex being
    # a prominence of 4 (prominence refers to the minimum height difference between neighboring peaks for a peak to
    # be considered prominent enough to be a QRS complex)
    # Can also use height, width, and distance between peaks as criteria, but prominence worked best
    # **** Stores array of the x-coordinates of detected qrs peaks in qrs_peaks
    qrs_peaks, locs = find_peaks(reconstructed_ECG, prominence=3.0, distance=90, height=2.0)

    # Store the y-values of the QRS complexes in an array by using the x-coordinates to find the ECG signal points in
    # the reconstructed ECG signal
    qrs_peak_values = reconstructed_ECG[qrs_peaks]

    # Store all the RR-intervals in an array by taking the difference between the x-values of all detected QRS complexes
    rr_intervals = []

    i = 0
    while i + 1 < len(qrs_peaks):
        rr_intervals.append(qrs_peaks[i + 1] - qrs_peaks[i])
        i = i + 1

    # THIRD GRAPH: Plot the regular, filter ECG signal, then plot all the detected QRS peaks with blue dots
    axs[2].plot(x, reconstructed_ECG, color='purple')
    axs[2].plot(qrs_peaks, reconstructed_ECG[qrs_peaks], "ob")
    plt.show()


# Filters original ECG signal and returns arrays of the x and y coordinates for all detected QRS complexes, along with
# the calculated RR intervals
# Creates and writes data for all detected QRS complexes to six CSV files (five files that correspond to each of the 5
# AAMI classes, and a sixth file that holds the QRS complexes that the code detected but that weren't labeled as
# R peaks by physician annotation, meaning they were wrongfully detected and can be discarded).
# Each file has 107,873 rows (total QRS complexes across all 48 MIT-BIH .dat records), and each row should have 187
# data points (93 points to the left of the R peak, the value of the R peak, 93 points to the right of the R peak).
# Data is based on the reconstructed ECG signal after filtering the original MIT-BIH signal used modwt(). DATA HAS NOT
# YET BEEN NORMALIZED to the range of 0 to 1. Functions for this step can be found in normalizeData.py, but this method
# needs to be run first.
def extract_features(record):
    # Parameters: record = name of MIT-BIH .dat file to process
    # sample_end = sample number to stop processing ECG signal at (can just delete this to process entire file)

    # Sig is a numpy array that stores raw ECG signal after reading in .dat file (only reads in first channel? ML11?)
    # annotation is the annotation object extracted from the physician annotaiton (.atr) file for an individual record.
    sig, fields = wfdb.rdsamp(record, channels=[0])
    annotation = wfdb.rdann(record, 'atr')
    # Store all the physician labels for each detected R peak in labels[] (use later for classifying each beat as
    # one of the five AAMI classes based on which label the R peak is associated with)
    labels = annotation.__dict__['symbol']

    # Use modwt() function to perform maximal overlap discrete wavelet transform on raw ECG signal
    # uses Symlet wavelets with 4 vanishing points (recommended for ECG signal) with 6 different scales (test which one
    # is ideal)
    wt = modwt(sig, 'sym4', 6)

    # Array to store coefficients that correspond to scale 2^3 for modwt (test different scales by plotting wavelets
    # from modwt to see which one gets rid of noise best)
    # For us, 3 or 4 seems best
    # 3
    reconstruct = np.zeros(shape(wt))
    reconstruct[3, :] = wt[3, :]

    # Use inverse function to create reconstructed ECG signal with data from scale 2^3
    reconstructed_ECG = imodwt(reconstruct, 'sym4')

    # Use find_peaks to detect the QRS complexes in the filtered ECG signal with the condition for a QRS complex being
    # a prominence of 4 (prominence refers to the minimum height difference between neighboring peaks for a peak to
    # be considered prominent enough to be a QRS complex)
    # Can also use height, width, and distance between peaks as criteria, but prominence worked best
    # **** Stores array of the x-coordinates of detected qrs peaks in qrs_peaks
    qrs_peaks, locs = find_peaks(reconstructed_ECG, prominence=3.0, distance=90, height=2.0)

    # Store the y-values of the QRS complexes in an array by using the x-coordinates to find the ECG signal points in
    # the reconstructed ECG signal
    qrs_peak_values = reconstructed_ECG[qrs_peaks]

    # Start of loop that goes through list of detected QRS peaks and adds 187 points for each QRS peak to one of six
    # arrays based on the physician label. 187 points are taken from reconstructed_ECG --> 93 points to the left of
    # QRS peak, then the point for the QRS peak, then the 93 points to the right.
    j = 0
    prev_r_peak_x = 0

    # Initialize 2d arrays for each of the 5 AAMI classes to hold all the 187 points for each detected QRS complex
    # in a record. Arrays have as many rows as the number of QRS complexes detected, and each row has the 187 points.
    # Sixth array ('oops') holds any QRS complexes that were detected by the code, but were not labeled by the
    # physician annotations, meaning there is no label / class associated with them (that data can be discarded,
    # usually very few points)
    # =====================================
    # Since each array is already initialized with 187 values of 0.0 in each row, in the end each array should have the
    # same number of rows (ex: 107,000), but only some rows will be filled with data, while other rows (in which the
    # that row's R peak corresponded to a different AAMI class) will still be filled with all 0.0). For example, say
    # the first 8 rows in non_ectopic are filled with data, but the 9th row is filled with all 0s. This means that the
    # data for the 9th row is in a different 2d array with the AAMI class that the physicians labeled for that row. If
    # we look at the first 9 rows of supravent, the first 8 rows are filled with all 0s (because the data for those
    # rows correspond to the non-ectopic AAMI class, meaning they're stored in non-ectopic), while the 9th row has
    # data, meaning that the data for the 9th row corresponds to the supraventricular AAMI class, and for all other
    # 2d arrays, the 9th row should have all 0.0s.
    non_ectopic = [[0.0] * 187] * len(qrs_peaks)
    supravent = [[0.0] * 187] * len(qrs_peaks)
    ventric = [[0.0] * 187] * len(qrs_peaks)
    fusion = [[0.0] * 187] * len(qrs_peaks)
    unknown = [[0.0] * 187] * len(qrs_peaks)
    oops = [[0.0] * 187] * len(qrs_peaks)

    # Beginning of loop!!!
    while j < len(qrs_peaks):

        # Set signal_points list to empty --> will hold the 187 points for each QRS complex, and resets to empty
        # each time the loop runs and moves on to the next QRS complex
        signal_points = []

        # Store the index of the current QRS complex (x-coordinate on graph)
        r_peak_x = qrs_peaks[j]
        # Store the distance between the current QRS complex and the previous one (for the first QRS complex, we set
        # the previous peak to 0, or the very first data point in the ECG signal) to check that the distance is at
        # least 93 (so we can get 93 data points)
        dist = r_peak_x - prev_r_peak_x

        # If the distance between the two R peaks is greater than or equal to 93, then just add the 93 points to the
        # left of the R peak to the signal points list.
        if dist >= 93:
            k = r_peak_x - 93
            while k < r_peak_x and k < len(reconstructed_ECG):
                signal_points.append(reconstructed_ECG[k])
                k = k + 1
        # If the distance between the two R peaks is less than 93, then calculate the difference between the actual
        # distance and 93, and pad the beginning of signal points with the needed number of 0s. Then, fill in the rest
        # of signal points with the available data points to the left of the R peak. (ensures that there is a fixed
        # length of data points for each QRS complex)
        else:
            k = r_peak_x - dist
            while k < (93 - dist) and k < len(reconstructed_ECG):
                signal_points.append(0.0)
                k = k + 1

            k = r_peak_x - dist
            while k < r_peak_x and k < len(reconstructed_ECG):
                signal_points.append(reconstructed_ECG[k])
                k = k + 1

        # Now, add the value of the R peak to the signal points list as the middle point (access from qrs_peak_values,
        # the list that holds the corresponding y-values for each detected R peak)
        signal_points.append(qrs_peak_values[j])

        # Now, store the x position of the next R peak so we can calculate the distance between the current and future
        # peaks. If the current R peak is the last detected R peak in the set, then set the future R peak to be the
        # last data point in the reconstructed ECG signal. Otherwise, just set the future R peak to the next detected
        # R peak in the list.
        if j == len(qrs_peaks) - 1:
            future_r_peak_x = reconstructed_ECG[len(reconstructed_ECG) - 1]
        else:
            future_r_peak_x = qrs_peaks[j+1]

        # Add the 93 points to the right of the detected R peak. Calculate the distance between the current R peak
        # and next R peak. If the distance is greater than 93, simply add the next 93 data points from the ECG signal
        # to the signal_points list. If the distance is less than 93, add all the available data points after the
        # R peak to signal_points, then pad the remaining spots with 0s (to ensure there are 93 data points).
        dist = future_r_peak_x - r_peak_x
        k = r_peak_x + 1
        if dist >= 93:
            while k < (r_peak_x + 93) and k < len(reconstructed_ECG):
                signal_points.append(reconstructed_ECG[k])
                k = k + 1
        else:
            while k < (r_peak_x + dist) and k < len(reconstructed_ECG):
                signal_points.append(reconstructed_ECG[k])
                k = k + 1
            initial_k = k
            while k < initial_k + 93 - dist and len(signal_points) < 186:
                signal_points.append(0.0)
                k = k + 1

        # Add the signal_points list as a row of 187 data points to one of the 6 2d arrays based on the physician label
        # associated with that R peak (get the label from the labels[] list which was taken from the .atr annotation
        # file associated with the record. Most of the AAMI classes have several possible labels associated with them,
        # so based on which category the label fits into, add the signal_points data to the corresponding 2d array.
        # If the index of the current R peak is within the range of the labels list (list of R peaks and list of
        # physician labels should be the same length if detected properly), then check for the appropriate label.
        # If not, that means the code detected an R peak that was not labeled by physicians and is therefore not
        # associated with any AAMI class, so add it to 'oops.csv'
        if j < len(labels):
            label = labels[j]

            if label == '+' or label == 'N' or label == 'L' or label == 'R' or label == 'e' or label == 'j':
                non_ectopic[j] = signal_points
            elif label == 'A' or label == 'a' or label == 'J' or label == 'S':
                supravent[j] = signal_points
            elif label == 'V' or label == '[' or label == '!' or label == ']' or label == 'E':
                ventric[j] = signal_points
            elif label == 'F':
                fusion[j] = signal_points
            elif label == '/' or label == 'f' or label == 'Q':
                unknown[j] = signal_points
            else:
                oops[j] = signal_points
        else:
            oops[j] = signal_points

        # Set new previous R peak to the current R peak and increase index of QRS peaks list (j) by 1 for the next
        # iteration of the loop.
        prev_r_peak_x = r_peak_x
        j = j + 1

    # Print out each row in the non-ectopic 2d array for testing (non-ectopic should contain the majority of the data
    # points)
    for row in non_ectopic:
        print("Num Signals: ", len(row))
        print(row)

    # Create a csv called 'Ndata' to store all the data from the non-ectopic 2d array. Use chmod to change the file
    # permissions so we are able to constantly write additional data to the file. Open the file with command 'a'
    # (append --> either creates a new file if there is no existing file with the name 'Ndata' or appends new data to
    # the pre-existing file if found). Write the rows as the CSV file as the arrays in the non_ectopic 2d array.
    # Just like with the non-ectopic 2d array, several rows in the Ndata.csv file will contain all 0.0s. This means that
    # the data for that index does not correspond to the non-ectopic AAMI class and is thus stored in a different CSV file.
    file_name = "Ndata.csv"
    os.chmod("Ndata.csv", 0o777)
    with open(file_name, 'a',  newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')

        csv_writer.writerows(non_ectopic)

    # Same process for 'Sdata.csv' --> holds all the data from supravent (supraventricular ectopic beats - Class S)
    file_name = "Sdata.csv"
    os.chmod("Sdata.csv", 0o777)
    with open(file_name, 'a',  newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')

        csv_writer.writerows(supravent)

    # Same process for 'Vdata.csv' --> holds all the data from ventric (ventricular ectopic beats - Class V)
    file_name = "Vdata.csv"
    os.chmod("Vdata.csv", 0o777)
    with open(file_name, 'a',  newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')

        csv_writer.writerows(ventric)

    # Same process for 'Fdata.csv' --> holds all the data from fusion (fusion beats - Class F)
    file_name = "Fdata.csv"
    os.chmod("Fdata.csv", 0o777)
    with open(file_name, 'a',  newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')

        csv_writer.writerows(fusion)

    # Same process for 'Qdata.csv' --> holds all the data from unknown (Unknown beats - Class Q)
    file_name = "Qdata.csv"
    os.chmod("Qdata.csv", 0o777)
    with open(file_name, 'a',  newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')

        csv_writer.writerows(unknown)

    # Same process for 'oops.csv' --> holds all the data from oops (R peaks that the code detected but were not
    # labeled by physicians, can be discared since not associated with any of the five AAMI classes)
    file_name = "oops.csv"
    os.chmod("oops.csv", 0o777)
    with open(file_name, 'a',  newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')

        csv_writer.writerows(oops)

    # Store all the RR-intervals in an array by taking the difference between the x-values of all detected QRS complexes
    rr_intervals = []

    i = 0
    while i + 1 < len(qrs_peaks):
        rr_intervals.append(qrs_peaks[i + 1] - qrs_peaks[i])
        #print(qrs_peaks[i + 1] - qrs_peaks[i])
        i = i + 1

    # Return the x values of the R peaks, the y values, and the distance between all the R peaks for testing
    return qrs_peaks, qrs_peak_values, rr_intervals


if __name__ == '__main__':


#    get_filtered_signal('mitdb/100')

    # Can call this function to test each record's QRS detection before extracting all the features with
    # extract_features(). Plot graphs from sample 0 to sample 3000, just to see if the code is accurately detecting
    # all the QRS complexes (represented by the dots in the 3rd graph). If not, edit the prominence, distance, and height
    # parameters for the find_peaks() function within plot_all_signals() until all QRS complexes are being detected,
    # then apply same changes to find_peaks() function in extract_features() before writing data to csv.
#    plot_all_signals('mitdb/234', 0, 3000)

    # Write filtered data with fixed number of points to represent each detected QRS complex for one record
    x_vals, y_vals, intervals = extract_features('mitdb/234')

    print("QRS Peak Locations: ", x_vals)
    print("QRS Peak Values: ", y_vals)
    print("RR Intervals: ", intervals)
    print("Num of QRS Complexes: ", len(x_vals))






