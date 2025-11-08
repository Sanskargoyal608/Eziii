import pandas as pd
import glob

def merge_scholarship_data():
    """
    Merges all scholarship .xlsx files from the 'data' directory into a single 'scholarship.csv' file.
    """
    data_path = 'data'
    # Use glob to find all .xlsx files in the data directory
    scholarship_files = glob.glob(f"{data_path}/*.xlsx")

    if not scholarship_files:
        print("No scholarship .xlsx files found in the 'data' directory.")
        return

    # List to hold dataframes
    df_list = []

    for file in scholarship_files:
        try:
            # Read each excel file
            df = pd.read_excel(file)
            df_list.append(df)
            print(f"Successfully read {file}")
        except Exception as e:
            print(f"Error reading {file}: {e}")

    if not df_list:
        print("No dataframes to merge.")
        return

    # Concatenate all dataframes
    merged_df = pd.concat(df_list, ignore_index=True)

    # Write the merged dataframe to a new CSV file
    output_file = f"{data_path}/scholarship.csv"
    try:
        merged_df.to_csv(output_file, index=False)
        print(f"Successfully merged {len(scholarship_files)} files into {output_file}")
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")

if __name__ == "__main__":
    merge_scholarship_data()
