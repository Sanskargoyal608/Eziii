import sqlite3
import pandas as pd
import json
import glob

DB_FILE = "federated_data.db"
CSV_FILE = "data/naukri_com-jobs__2020.csv"
SCHOLARSHIP_CSV_FILE = "data/scholarship.csv"

def populate_sqlite_data():
    """Populates the SQLite database with job data from a local CSV file."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            print("Connected to SQLite database to populate data.")

            # Load the dataset from local CSV
            print(f"Loading data from '{CSV_FILE}'...")
            try:
                df = pd.read_csv(CSV_FILE)
                df.columns = df.columns.str.strip()
                print("Data loaded successfully.")
            except FileNotFoundError:
                print(f"ERROR: The file '{CSV_FILE}' was not found in the 'e:\\Eziii\\eziii_backend' directory.")
                print("Please download the CSV file from Kaggle and place it in that directory.")
                return

            cursor.execute("DELETE FROM govt_jobs")
            print("Cleared existing data from 'govt_jobs'.")

            # --- Populate govt_jobs table ---
            jobs_to_insert = []
            skipped_rows = 0
            for index, row in df.iterrows():
                job_title = row.get('Job Title')
                if job_title and isinstance(job_title, str) and job_title.strip():
                    eligibility_criteria = {
                        "skills": row.get('Key Skills') if not pd.isna(row.get('Key Skills')) else None,
                        "experience": row.get('Job Experience Required') if not pd.isna(row.get('Job Experience Required')) else None,
                        "salary": row.get('Job Salary') if not pd.isna(row.get('Job Salary')) else None
                    }
                    
                    # Construct job_description from other fields
                    job_description = (
                        f"Functional Area: {row.get('Functional Area', 'N/A')}, "
                        f"Industry: {row.get('Industry', 'N/A')}, "
                        f"Role: {row.get('Role', 'N/A')}"
                    )
                    
                    jobs_to_insert.append((
                        job_title,
                        job_description,
                        row.get('Location'),
                        row.get('Crawl Timestamp'),  # Use Crawl Timestamp for posted_date
                        "https://www.naukri.com/",
                        json.dumps(eligibility_criteria)
                    ))
                else:
                    skipped_rows += 1
            
            if skipped_rows > 0:
                print(f"Skipped {skipped_rows} rows due to missing job title.")

            cursor.executemany("""
            INSERT INTO govt_jobs (job_title, job_description, location, posted_date, source_url, eligibility_criteria)
            VALUES (?, ?, ?, ?, ?, ?)
            """, jobs_to_insert)
            print(f"Inserted {len(jobs_to_insert)} records into 'govt_jobs'.")

            conn.commit()
            print("Data committed and connection closed.")

    except (sqlite3.Error, Exception) as e:
        print(f"An error occurred: {e}")

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

def populate_scholarship_data():
    """Populates the SQLite database with scholarship data from a local CSV file."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            print("Connected to SQLite database to populate scholarship data.")

            # Load the dataset from local CSV
            print(f"Loading data from '{SCHOLARSHIP_CSV_FILE}'...")
            try:
                df = pd.read_csv(SCHOLARSHIP_CSV_FILE)
                print("Data loaded successfully.")
            except FileNotFoundError:
                print(f"ERROR: The file '{SCHOLARSHIP_CSV_FILE}' was not found in the 'e:\\Eziii\\eziii_backend' directory.")
                return

            # --- Populate scholarships table ---
            scholarships_to_insert = []
            for index, row in df.iterrows():
                scholarship_name = row.get('Name')
                if scholarship_name and isinstance(scholarship_name, str) and scholarship_name.strip():
                    eligibility_criteria = {
                        "education_qualification": row.get('Education Qualification'),
                        "gender": row.get('Gender'),
                        "community": row.get('Community'),
                        "religion": row.get('Religion'),
                        "exservice_men": row.get('Exservice-men'),
                        "disability": row.get('Disability'),
                        "sports": row.get('Sports'),
                        "annual_percentage": row.get('Annual-Percentage'),
                        "income": row.get('Income'),
                        "india": row.get('India')
                    }
                    scholarships_to_insert.append((
                        scholarship_name,
                        f"A scholarship for {row.get('Education Qualification')} students.",
                        json.dumps(eligibility_criteria)
                    ))

            cursor.executemany("""
            INSERT INTO Scholarships (scholarship_name, description, eligibility_criteria)
            VALUES (?, ?, ?)
            """, scholarships_to_insert)
            print(f"Inserted {len(scholarships_to_insert)} records into 'Scholarships'.")

            conn.commit()
            print("Data committed and connection closed.")

    except (sqlite3.Error, Exception) as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    merge_scholarship_data()
    populate_sqlite_data()
    populate_scholarship_data()