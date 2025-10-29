import os
import numpy as np
import tifffile
import pandas as pd
import matplotlib.pyplot as plt

from skimage.exposure import rescale_intensity

def ask_user_mask_mapping(mask, mask_path):
    # Map 1 to 0.5 (gray) and 2 to 1 (white)
    display_mask = mask.astype(float).copy()
    display_mask[mask == 1] = 0.5
    display_mask[mask == 2] = 1.0

    plt.imshow(np.max(display_mask, axis=0), cmap='gray', vmin=0, vmax=1)
    plt.title(mask_path)
    plt.show()

    while True:
        answer = input(
            "Is 1 (gray) inside nucleus or outside? "
            "Options: 1 means inside=gray, outside=white; 2 means inside=white, outside=gray; inside_1 means inside only=gray; inside_2 means inside only=while; outside_1 means outside only=gray; outside_2 means outside only=white: "
        ).strip()
        if answer in ['1', '2', 'inside_1', 'inside_2', 'outside_1', 'outside_2']:
            return answer

def compute_fluorescent_density(image_stack, mask_stack, region_value, background):
    masked = (mask_stack == region_value)
    voxel_values = image_stack[masked]
    if voxel_values.size == 0:
        return np.nan
    return np.sum(voxel_values - background) / voxel_values.size

def process_directory(current_dir):
    roi_dir = os.path.join(current_dir, 'Cut ROI')
    mask_dir = os.path.join(current_dir, 'Masks')
    inside_dir = os.path.join(current_dir, 'Partition coefficient crop inside')
    outside_dir = os.path.join(current_dir, 'Partition coefficient crop outside')

    nuclear_data = []
    cytoplasmic_data = []

    for filename in os.listdir(roi_dir):
        if not filename.endswith('.tif'):
            continue

        roi_path = os.path.join(roi_dir, filename)
        mask_path = os.path.join(mask_dir, filename)
        inside_crop_path = os.path.join(inside_dir, filename)
        outside_crop_path = os.path.join(outside_dir, filename)

        roi_img = tifffile.imread(roi_path)
        # Assume 3D + channel, take 488 nm channel (index 1)
        channel = roi_img.shape[0]  # z slices
        if roi_img.ndim == 4:  # z, ch, y, x
            signal = roi_img[:, 0, :, :]  # 488nm
        elif roi_img.ndim == 3:
            signal = roi_img  # single-channel

        background = np.min(signal)

        # Check if mask exists
        if os.path.exists(mask_path):
            mask = tifffile.imread(mask_path)
            user_input = ask_user_mask_mapping(mask, mask_path)

            if user_input == '1':
                inside_val, outside_val = 1, 2
            elif user_input == '2':
                inside_val, outside_val = 2, 1
            elif user_input == 'inside_1':
                inside_val, outside_val = 1, None
            elif user_input == 'inside_2':
                inside_val, outside_val = 2, None
            elif user_input == 'outside_1':
                inside_val, outside_val = None, 1 
            elif user_input == 'outside_2':
                inside_val, outside_val = None, 2 

            # Nuclear condensate density
            if inside_val is not None:
                nuclear_dens = compute_fluorescent_density(signal, mask, inside_val, background)
                if os.path.exists(inside_crop_path):
                    inside_crop_img = tifffile.imread(inside_crop_path)
                    inside_crop = inside_crop_img[:, 0, :, :] # 561 nm
                    dilute_dens = np.sum(inside_crop - background) / inside_crop.size
                    partition_coeff = nuclear_dens / dilute_dens if dilute_dens > 0 else np.nan
                else:
                    dilute_dens = partition_coeff = np.nan
                nuclear_data.append([filename, nuclear_dens, dilute_dens, partition_coeff])

            # Cytoplasmic condensate density
            if outside_val is not None:
                cytoplasmic_dens = compute_fluorescent_density(signal, mask, outside_val, background)
                if os.path.exists(outside_crop_path):
                    outside_crop_img = tifffile.imread(outside_crop_path)
                    outside_crop = outside_crop_img[:, 0, :, :] # 561 nm
                    dilute_dens = np.sum(outside_crop - background) / outside_crop.size
                    partition_coeff = cytoplasmic_dens / dilute_dens if dilute_dens > 0 else np.nan
                else:
                    dilute_dens = partition_coeff = np.nan
                cytoplasmic_data.append([filename, cytoplasmic_dens, dilute_dens, partition_coeff])

    # Save results
    nuclear_df = pd.DataFrame(nuclear_data, columns=[
        'file name', 'nuclear condensate density', 'nuclear dilute density', 'nuclear partition coefficient'
    ])
    cytoplasmic_df = pd.DataFrame(cytoplasmic_data, columns=[
        'file name', 'cytoplasmic condensate density', 'cytoplasmic dilute density', 'cytoplasmic partition coefficient'
    ])

    base_name = os.path.basename(os.path.abspath(current_dir))
    nuclear_df.to_csv(os.path.join(current_dir, f"{base_name}_Partition coefficient_nuclear.csv"), index=False)
    cytoplasmic_df.to_csv(os.path.join(current_dir, f"{base_name}_Partition coefficient_cytoplasmic.csv"), index=False)

    print("✓ Done processing:", current_dir)

# Example usage
if __name__ == '__main__':
    import sys
    # directory = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    directory = 'C:/Users/sjtu_/Box/2. Lab/Condensate Volume Quantification/JABr MS2_mCherry/'
    process_directory(directory)
