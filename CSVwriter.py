import pygame
import csv
import pandas as pd
import locale


class CSVwriter():
    def __init__(self):
        self.dataOutputFolder = "Data/"
        self.dataInputFolder = "SimulatedData/"
        self.delimiter = self.detect_excel_friendly_delimiter()

    def detect_excel_friendly_delimiter(self):
        """
        Return ';' if the system uses ',' as decimal separator,
        otherwise return ','.
        """
        try:
            locale.setlocale(locale.LC_NUMERIC, "")
        except Exception:
            pass

        decimal = locale.localeconv().get("decimal_point", ".")
        return ";" if decimal == "," else ","

    def save_dict_to_csv(self, file_name, field_names, data_dict, mean_row=None):
        # Define the field names (header) for your CSV file

        file_path = self.dataOutputFolder + file_name

        # Open the CSV file for writing
        with open(file_path, mode='w', newline='') as file:
            # Create a CSV writer object
            delimiter = self.detect_excel_friendly_delimiter()
            writer = csv.DictWriter(file, fieldnames=field_names, delimiter=delimiter, lineterminator='\r\n')


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

            if mean_row is not None:
                writer.writerow(mean_row)

        print(f'Data written to ' + file_path)

    def save_list_to_csv(self, data, file_name):

        file_path = self.dataOutputFolder + file_name

        df = pd.DataFrame(data)

        df.to_csv(file_path, sep=self.delimiter, header=False, index=False)
        print(f'Data written to ' + file_path)

    def save_coinsList_to_csv(self, data, file_name, column_names=None, index_name=None):

        file_path = self.dataOutputFolder + file_name

        df = pd.DataFrame(data)

        # Set column names if provided
        if column_names:
            df.columns = column_names

        # Set index name if provided
        if index_name:
            df.index.name = index_name

        df.to_csv(file_path, sep=self.delimiter, header=False, index=False)
        print(f'Data written to ' + file_path)

    def read_csv(self, file_name):
        file_path = self.dataInputFolder + file_name
        df = pd.read_csv(file_path, sep=self.delimiter)
        return df
