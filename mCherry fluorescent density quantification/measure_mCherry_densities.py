#!/usr/bin/env python3
import numpy as np
from tifffile import imread
import csv
from pathlib import Path

def safe_density(total_sum, voxels):
    return float(total_sum) / voxels if voxels > 0 else np.nan

def compute_metrics(img_path, nucleus_mask_path, wholecell_mask_path):
    # Load
    img = imread(img_path).astype(np.float64)
    m0 = imread(nucleus_mask_path)
    m2 = imread(wholecell_mask_path)

    # Sanity check
    if img.shape != m0.shape or img.shape != m2.shape:
        raise ValueError(f"Shape mismatch: image {img.shape}, nucleus mask {m0.shape}, cell mask {m2.shape}")

    # Boolean masks
    nucleus_mask = m0 > 0
    wholecell_mask = m2 > 0
    cytoplasm_mask = np.logical_and(wholecell_mask, np.logical_not(nucleus_mask))

    # Sums
    sum_nucleus = np.sum(img[nucleus_mask])
    sum_cyto = np.sum(img[cytoplasm_mask])
    vox_nucleus = np.count_nonzero(nucleus_mask)
    vox_cyto = np.count_nonzero(cytoplasm_mask)

    # Densities
    dens_nucleus = safe_density(sum_nucleus, vox_nucleus)
    dens_cyto = safe_density(sum_cyto, vox_cyto)

    # Ratio
    total = sum_nucleus + sum_cyto
    ratio = sum_nucleus / total if total > 0 else np.nan

    return {
        "sum_nucleus": sum_nucleus,
        "voxels_nucleus": vox_nucleus,
        "fluorescence_density_nucleus": dens_nucleus,
        "sum_cytoplasm": sum_cyto,
        "voxels_cytoplasm": vox_cyto,
        "fluorescence_density_cytoplasm": dens_cyto,
        "nucleus_ratio": ratio
    }

def main():
    print("Enter the full path for each file:")
    nucleus_mask = input("1️⃣  C=0 nucleus mask file: ").strip('" ')
    cell_mask = input("2️⃣  C=2 whole-cell mask file: ").strip('" ')
    image_file = input("3️⃣  C=2 fluorescence image file: ").strip('" ')

    nucleus_mask = Path(nucleus_mask)
    cell_mask = Path(cell_mask)
    image_file = Path(image_file)

    metrics = compute_metrics(image_file, nucleus_mask, cell_mask)

    print("\n✅ Results:")
    for k, v in metrics.items():
        print(f"{k:35s} : {v}")

    # Optional: save to CSV
    save = input("\nSave results to CSV? (y/n): ").strip().lower()
    if save == "y":
        csv_path = image_file.with_suffix(".csv")
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["metric", "value"])
            for k, v in metrics.items():
                writer.writerow([k, v])
        print(f"Saved results → {csv_path}")

if __name__ == "__main__":
    main()
