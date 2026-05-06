import os
import shutil


def reorganize_for_yolo(split_name):
    base_path = f"data/{split_name}"
    img_target = os.path.join(base_path, "images")
    lbl_target = os.path.join(base_path, "labels")

    os.makedirs(img_target, exist_ok=True)
    os.makedirs(lbl_target, exist_ok=True)

    class_folders = [
        f for f in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, f)) and f not in ["images", "labels"]
    ]

    for folder in class_folders:
        folder_path = os.path.join(base_path, folder)

        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)

            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                shutil.move(file_path, os.path.join(img_target, file))
            elif file.lower().endswith(".txt"):
                shutil.move(file_path, os.path.join(lbl_target, file))

        os.rmdir(folder_path)

    print(f"{split_name} terminé")


for s in ["train", "val", "test"]:
    path = f"data/{s}"
    if os.path.exists(path):
        reorganize_for_yolo(s)