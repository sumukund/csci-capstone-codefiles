import cv2
import numpy as np
import os
import re
from collections import defaultdict

IMAGE_FOLDER = "images"

def group_images(folder):
    groups = defaultdict(list)

    pattern = re.compile(r".*_(\d+)_\d+\.JPG")

    for file in os.listdir(folder):
        match = pattern.match(file)
        if match:
            group_id = match.group(1)
            groups[group_id].append(os.path.join(folder, file))

    return groups

def compute_illuminated_average(image_paths):
    if not image_paths:
        return None

    first = cv2.imread(image_paths[0])
    h, w = first.shape[:2]
    accum = np.zeros(first.shape, np.float32)

    count = 0

    for path in image_paths:
        img = cv2.imread(path)
        if img is None:
            continue
        if img.shape[:2] != (h, w):
            if img.shape[:2] == (w, h):
                img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
            else:
                img = cv2.resize(img, (w, h))
        accum += img.astype(np.float32)
        count += 1

    if count == 0:
        return None

    avg = accum / count
    return np.uint8(avg)


# -----------------------------
# 3. RUN FOR ALL GROUPS
# -----------------------------
def process_all_groups(folder):
    groups = group_images(folder)

    results = {}

    for group_id, images in groups.items():
        print(f"Processing group {group_id} ({len(images)} images)")
        avg_img = compute_illuminated_average(images)

        if avg_img is not None:
            results[group_id] = avg_img

            # Save output
            out_path = f"avg_{group_id}.jpg"
            cv2.imwrite(out_path, avg_img)
            print(f"Saved {out_path}")

    return results


def main():
   process_all_groups("images")
 
if __name__ == "__main__":
    main()