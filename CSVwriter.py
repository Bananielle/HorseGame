import pygame
import csv
import pandas as pd

class CSVwriter():
    def __init__(self):
        self.dataOutputFolder = "Data/"
        self.dataInputFolder = "SimulatedData/"

    def save_dict_to_csv(self, file_name, field_names, data_dict):
        # Define the field names (header) for your CSV file

        file_path = self.dataOutputFolder + file_name

        # Open the CSV file for writing
        with open(file_path, mode='w', newline='') as file:
            # Create a CSV writer object
            writer = csv.DictWriter(file, fieldnames=field_names)

            # Write the header row
            writer.writeheader()

            max_length = max(len(data_dict[key]) for key in field_names)
            for i in range(max_length):
                row = {}
                for key in field_names:
                    if i < len(data_dict[key]):
                        row[key] = data_dict[key][i]
                    else:
                        row[key] = None  # or some other placeholder value
                writer.writerow(row)

        print(f'Data written to ' + file_path)


    def save_list_to_csv(self, data, file_name):

        file_path = self.dataOutputFolder + file_name

        df = pd.DataFrame(data)

        # Write to CSV
        #with open(file_path, 'w', newline='') as file:
         #   writer = csv.writer(file)
          #  writer.writerows(data)

        df.to_csv(file_path,header=False, index=False)
        print(f'Data written to ' + file_path)

    def read_csv(self, file_name):
        file_path = self.dataInputFolder + file_name
        df = pd.read_csv(file_path)
        return df

