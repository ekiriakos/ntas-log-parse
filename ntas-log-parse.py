import csv
import json
import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import datetime

#root = tk.Tk()
#root.withdraw()

#file_path = filedialog.askopenfilename()

#print(file_path)

# TODO: Parse logs as taken from kubectl logs.
#       Do not overwrite csv - export it to file named after original.
#       Re-factor with pandas
#       Add file browser GUI to select input.
#       Add exported file "Save as" GUI.
#       List error levels found (error, warning, info etc.) and count of each.
#       Add radio button to select desired error level and export only this to csv.

############# NOTES ############
#  There are 3 types of logs and 2 formats:
#  1. activeAlarms, alarmHistory
#  2. event_logs
#####################################

menu = """

Please select one of the following options:

1) Save NTAS alarms (json) to CSV.
2) Save NTAS event logs (json) to CSV.
3) Save kubectl logs from infra node to CSV.
4) Exit

NOTE: Exported files must be placed in "logs" directory.

Your selection: """

############# ALARMS ################

# Return json from NTAS activeAlarms.json or alarmHistory.json
def log_to_json(logfile):
    with open(logfile, "r") as lf:
        data = json.load(lf)
    return data

# Find number of alarms in extracted json
def alarm_count(alarmfile):
    data = log_to_json(alarmfile)
    return "Number of alarms is : {}".format(data['total'])

# Create list of alarms from extracted json
def alarms_to_list(alarms_json):
    alarm_list = []
    for i, k in alarms_json.items():
        if i == 'alarms':
            for dic in alarms_json['alarms']:
                alarm_list.append(dic)
    return alarm_list

# Save alarms to csv
def parse_alarms(alarm_list):
    column_names = []
    parsed_list = []
    #csv_file = "alarms.csv"
    csv_file = input_file + ".csv"

    for alarm in alarm_list:
        parsed_dict = {}
        for i, k in alarm.items():
            if i == 'alarm':
                for j, l in alarm[i].items():
                    parsed_dict[j] = l
                    if j not in column_names:
                        column_names.append(j)
            else:
                parsed_dict[i] = k
            if i not in column_names:
                column_names.append(i)
        #print(parsed_dict)
        parsed_list.append(parsed_dict)

    #for index, item in enumerate(parsed_list):
    #    print(index, item)

    column_names.remove('alarm')

    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=column_names)
        writer.writeheader()
        for data in parsed_list:
            writer.writerow(data)

    print("\n ==== Finished writing to csv ====")

    return column_names


########## EVENTS #############

def events_to_jsonlist(eventfile):
    column_names = []
    parsed_list = []
    # Return a dict for each alarm
    with open(eventfile, "r") as ef:
        events = json.loads("[" + ef.read().replace("}\n{", "},\n{") + "]")

    for event in events:
        parsed_dict = {}
        for i, k in event.items():
            if i == 'log':
                for j, l in event[i].items():
                    # print("{} %% {}".format(j,l))
                    parsed_dict[j] = l
                    if j not in column_names:
                        column_names.append(j)
            else:
                parsed_dict[i] = k
            if i not in column_names:
                column_names.append(i)
        # print(parsed_dict)
        parsed_list.append(parsed_dict)

    #for index, item in enumerate(parsed_list):
     #   print(index, item)

    column_names.remove('log')

    return parsed_list

def parse_events(event_list):

    column_names = []
    parsed_list = []
    csv_file = "events.csv"
    
    for event in event_list:
        parsed_dict = {}
        for i, k in event.items():
            if i == 'log':
                for j, l in event[i].items():
                    #print("{} %% {}".format(j,l))
                    parsed_dict[j] = l
                    if j not in column_names:
                        column_names.append(j)
            else:
                parsed_dict[i] = k
            if i not in column_names:
                column_names.append(i)
        #print(parsed_dict)
        parsed_list.append(parsed_dict)

    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=column_names)
        writer.writeheader()
        for data in parsed_list:
            writer.writerow(data)

    print("================================")

    return column_names

def check_file_path(filename):
    full_path = Path.cwd().joinpath('logs', filename)
    if full_path.exists():
        return full_path
    else:
        return None


while (user_input := input(menu)) != '4':
    if user_input == '1':
        input_file = input("Alarms filename: ")
        if check_file_path(input_file):
            with open(check_file_path(input_file), "r") as af:
                data = json.load(af)
            a_list = alarms_to_list(data)
            parse_alarms(a_list)
        else:
            print('Make sure the log file exists and is placed in the "logs" directory!')
    elif user_input == '2':
        input_file = input("Event logs filename: ")
        if check_file_path(input_file):
            el_json = events_to_jsonlist(check_file_path(input_file))
            parse_events(el_json)
        else:
            print('Make sure the log file exists and is placed in the "logs" directory!')
    elif user_input == '3':
        pass
    else:
        print("\nInvalid option, please try again.\n")

