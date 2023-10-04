import pygame
import csv

class CSVwriter():
    def __init__(self):
        self.datafolder = "Data/"

    def save_dict_to_csv(self, file_name, field_names, data_dict):
        # Define the field names (header) for your CSV file

        file_path = self.datafolder + file_name

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

