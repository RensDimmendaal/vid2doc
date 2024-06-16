from pathlib import Path
import cv2
import os
import sys
from tqdm import tqdm
import imagehash
import os
from collections import deque
from PIL import Image
from tqdm import tqdm

def resize_image_frame(frame, resize_width):
    ht, wd, _ = frame.shape
    new_height = resize_width * ht / wd
    frame = cv2.resize(frame, (resize_width, int(new_height)), interpolation=cv2.INTER_AREA)

    return frame

def extract_frames(
    video_path,
    output_dir_path: Path,
    type_bgsub: str = "MOG2",
    history: int = 15,
    threshold: int = 96,
    MIN_PERCENT_THRESH: float = 0.15,
    MAX_PERCENT_THRESH: float = 0.01,
    frame_rate=1,
):
    if type_bgsub == "GMG":
        raise NotImplementedError("GMG is not implemented yet")

    elif type_bgsub == "MOG2":
        bg_sub = cv2.createBackgroundSubtractorMOG2(
            history=history, varThreshold=16, detectShadows=False
        )
    elif type_bgsub == "KNN":
        bg_sub = cv2.createBackgroundSubtractorKNN(
            history=history, dist2Threshold=threshold, detectShadows=False
        )
    else:
        raise ValueError("Please choose GMG or KNN as background subtraction method")

    capture_frame = False
    screenshots_count = 0

    # Capture video frames.
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Unable to open video file: ", video_path)
        sys.exit()

    frame_no = 0
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    prog_bar = tqdm(total=num_frames)

    # Loop over subsequent frames.
    while cap.isOpened():
        ret, frame = cap.read()
        frame_no += 1

        if not ret:
            break
        if frame_no % frame_rate != 0:
            prog_bar.update(1)
            continue

        # Create a copy of the original frame.
        orig_frame = frame.copy()
        # Resize the frame keeping aspect ratio.
        frame = resize_image_frame(frame, resize_width=640)

        # Apply each frame through the background subtractor.
        fg_mask = bg_sub.apply(frame)

        # Compute the percentage of the Foreground mask.
        p_non_zero = (cv2.countNonZero(fg_mask) / (1.0 * fg_mask.size)) * 100

        # %age of non-zero pixels < MAX_PERCENT_THRESH, implies motion has stopped.
        # Therefore, capture the frame.
        if p_non_zero < MAX_PERCENT_THRESH and not capture_frame:
            capture_frame = True

            screenshots_count += 1

            # Get the current time in seconds and format it with leading zeroes.
            time_in_seconds = str(int(frame_no / fps)).zfill(4)
            jpg_fname = f"{time_in_seconds}.jpg"
            out_file_path = output_dir_path / jpg_fname
            cv2.imwrite(out_file_path, orig_frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
            prog_bar.set_postfix_str(f"Total Screenshots: {screenshots_count}")

        # p_non_zero >= MIN_PERCENT_THRESH, indicates motion/animations.
        # Hence wait till the motion across subsequent frames has settled down.
        elif capture_frame and p_non_zero >= MIN_PERCENT_THRESH:
            capture_frame = False

        prog_bar.update(1)

    # Release progress bar and video capture object.
    prog_bar.close()
    cap.release()


def remove_duplicates(base_dir, hash_size=8, hashfunc=imagehash.dhash, queue_len=5, threshold=4):
    _, duplicates = find_similar_images(
        base_dir,
        hash_size=hash_size,
        hashfunc=hashfunc,
        queue_len=queue_len,
        threshold=threshold,
    )

    if not len(duplicates):
        pass
    else:
        for dup_file in duplicates:
            file_path = os.path.join(base_dir, dup_file)

            if os.path.exists(file_path):
                os.remove(file_path)
            else:
                raise FileNotFoundError(f"Filepath: {file_path} does not exist.")




def find_similar_images(base_dir, hash_size=8, hashfunc=imagehash.dhash, queue_len=5, threshold=4):
    snapshots_files = sorted(os.listdir(base_dir))

    hash_dict = {}
    hash_queue = deque([], maxlen=queue_len)
    duplicates = []
    num_duplicates = 0

    with tqdm(snapshots_files) as t:
        for file in t:
            read_file = Image.open(os.path.join(base_dir, file))
            comp_hash = hashfunc(read_file, hash_size=hash_size)
            duplicate = False

            if comp_hash not in hash_dict:
                hash_dict[comp_hash] = file
                # Compare with hash queue to find out potential duplicates
                for img_hash in hash_queue:
                    if img_hash - comp_hash <= threshold:
                        duplicate = True
                        break

                if not duplicate:
                    hash_queue.append(comp_hash)
            else:
                duplicate = True

            if duplicate:
                duplicates.append(file)
                num_duplicates += 1
                t.set_postfix_str(f"Duplicate files: {num_duplicates}")

    return hash_dict, duplicates


def remove_duplicates(base_dir, hash_size=8, hashfunc=imagehash.dhash, queue_len=5, threshold=4):
    _, duplicates = find_similar_images(
        base_dir,
        hash_size=hash_size,
        hashfunc=hashfunc,
        queue_len=queue_len,
        threshold=threshold,
    )

    if not len(duplicates):
        print("No duplicates found!")
    else:
        print("Removing duplicates...")

        for dup_file in duplicates:
            file_path = os.path.join(base_dir, dup_file)

            if os.path.exists(file_path):
                os.remove(file_path)
            else:
                print("Filepath: ", file_path, "does not exists.")

        print("All duplicates removed!")

    print("***" * 10, "\n")
