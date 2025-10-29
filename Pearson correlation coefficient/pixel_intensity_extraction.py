import numpy as np
import tifffile
import pandas as pd

# Load the tiff file (replace this with the actual file path)
tiff_file = ''

image = tifffile.imread(tiff_file)

# Split the image into the two channels
channel_488nm = image[1]
channel_561nm = image[0]

# Find the indices where the intensity in the first channel is not zero
non_zero_indices = np.nonzero(channel_488nm)

# Extract the intensities from both channels at these indices
intensities_488nm = channel_488nm[non_zero_indices]
intensities_561nm = channel_561nm[non_zero_indices]

# Combine the intensities into a DataFrame
data = pd.DataFrame({
    '488nm_intensity': intensities_488nm,
    '561nm_intensity': intensities_561nm
})

print(data)

# Save to CSV
output_csv = ""
data.to_csv(output_csv, index=False)

print(f"Data has been saved to {output_csv}")