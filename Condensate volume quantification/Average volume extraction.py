import os
import pandas as pd
import re

def fix_typo_in_filenames(folder_path, typo='Smaple', correct='Sample'):
    for filename in os.listdir(folder_path):
        if typo in filename:
            new_filename = filename.replace(typo, correct)
            src = os.path.join(folder_path, filename)
            dst = os.path.join(folder_path, new_filename)
            os.rename(src, dst)
            print(f"Renamed: {filename} -> {new_filename}")


def process_folder(folder_path, location_label):
    results = []
    for filename in os.listdir(folder_path):
        # if filename.endswith('.xls') and re.search(r'(sample|Sample)\d+_\d+_\d+_' + location_label, filename):
        if filename.endswith('.xls'):
            file_path = os.path.join(folder_path, filename)
            try:
                df = pd.read_excel(file_path, skiprows=1)
                                
                # Make sure there's at least 5 columns
                if df.shape[1] < 5:
                    print(f"Warning: Less than 5 columns in {filename}")
                    continue

                if "Volume" not in df.columns:
                    print(f"Warning: 'Volume' column not found in {filename}")
                    continue

                # Get the class column by index (5th column = index 4)
                class_col = df.columns[4]
                df_valid = df[["Volume", class_col]].dropna()

                # Group by class and compute average volume
                grouped = df_valid.groupby(class_col)["Volume"].mean().reset_index()

                # Extract standardized cell name
                match = re.search(r'(sample|Sample\d+_\d+_\d+)', filename)
                if match:
                    cell_name = match.group(0) + "_" + location_label
                else:
                    cell_name = filename.replace('.xls', '')

                for _, row in grouped.iterrows():
                    results.append({
                        "Cell": cell_name,
                        "Class": row[class_col],
                        "Average volume": row["Volume"]
                    })

            except Exception as e:
                print(f"Error processing {filename}: {e}")
    return pd.DataFrame(results)

# # Example usage:
# base_dir = 'C:/Users/sjtu_/Box/2. Lab/Condensate Volume Quantification/Statistics/ABPP - statistics/'
# inside_dir = os.path.join(base_dir, 'inside')
# outside_dir = os.path.join(base_dir, 'outside')

# fix_typo_in_filenames(inside_dir)
# fix_typo_in_filenames(outside_dir)

# Define your base directory
base_dir = 'C:/Users/sjtu_/Box/2. Lab/Condensate Volume Quantification/Statistics/JAMango - statistics/'

# Process both inside and outside folders
inside_df = process_folder(os.path.join(base_dir, 'inside'), 'inside')
outside_df = process_folder(os.path.join(base_dir, 'outside'), 'outside')

# Save results
inside_df.to_csv(os.path.join(base_dir, 'inside.csv'), index=False)
outside_df.to_csv(os.path.join(base_dir, 'outside.csv'), index=False)
