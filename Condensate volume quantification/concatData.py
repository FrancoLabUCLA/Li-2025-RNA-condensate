import pandas as pd
from glob import glob
import os

def main():
    split_char = '_'
    files = glob('./*.xls')

    if not files:
        print("No .xls files found in the directory.")
        return

    basdir, basename = os.path.split(files[0])
    # Uncomment if you want to modify the basename
    # fname, fext = os.path.splitext(basename)
    # splitname = fname.split(split_char)
    # fname_short = splitname[:-2]
    # fname_short = split_char.join(fname_short)

    df = pd.DataFrame()

    for file in files:
        read_file = pd.read_excel(file)
        df = pd.concat([df, read_file], sort=False)

    df = df.reset_index(drop=True)

    output_file = os.path.join(basdir, 'allMeasurements.csv')
    df.to_csv(output_file, index=False)

    print(f"All .xls files have been concatenated and saved to {output_file}")

if __name__ == '__main__':
    main()