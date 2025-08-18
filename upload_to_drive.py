# @title ☁️ Upload File or Folder to Google Drive (Auto Rename)

input_path = ""  # @param {type:"string"}
drive_target_folder = "/content/drive/mydrive"  # @param {type:"string"}

import os, shutil, sys, datetime, time


# ✅ Logging
def log(message, level="INFO"):
    print(f"[{level}] {message}")


# ✅ Print file upload summary
def print_file_summary(index, total, filename, size_mb, dest_path, upload_time):
    log(f"Uploaded ({index}/{total}): {filename}", "SUCCESS")
    print(f"   Size     : {size_mb:.2f} MB")
    print(f"   Location : {dest_path}")
    print(f"   Time     : {upload_time}\n")


# ✅ Check & mount Google Drive
def check_drive():
    if not os.path.exists("/content/drive"):
        log("Google Drive is not mounted, mounting now...", "WARNING")
        from google.colab import drive

        drive.mount("/content/drive")
        log("Google Drive mounted successfully", "SUCCESS")
    else:
        log("Google Drive is already mounted", "INFO")


# ✅ Get list of files from input
def get_file_list(input_path: str):
    if not os.path.exists(input_path):
        log(f"Input path not found: {input_path}", "ERROR")
        sys.exit()

    if os.path.isfile(input_path):
        log("Input mode: Single file")
        return [os.path.basename(input_path)], os.path.dirname(input_path)

    elif os.path.isdir(input_path):
        files = [
            f
            for f in os.listdir(input_path)
            if os.path.isfile(os.path.join(input_path, f))
        ]
        log(f"Input mode: Folder with {len(files)} files")
        return files, input_path

    else:
        log("Invalid input path", "ERROR")
        sys.exit()


# ✅ Create target folder if not exists
def ensure_target_folder(folder: str):
    if not os.path.exists(folder):
        os.makedirs(folder)
        log(f"Target folder created: {folder}")
    else:
        log(f"Target folder found: {folder}")


# ✅ Upload files with auto rename
def upload_files(file_list, src_dir, dest_dir):
    if not file_list:
        log("No files found at the specified location", "WARNING")
        sys.exit()

    log(f"Uploading {len(file_list)} file(s) to Google Drive...\n")
    start_time = time.time()

    for i, filename in enumerate(file_list, 1):
        local_path = os.path.join(src_dir, filename)
        name_only, ext = os.path.splitext(filename)
        dest_path = os.path.join(dest_dir, filename)

        counter = 1
        while os.path.exists(dest_path):
            new_name = f"{name_only}_{counter}{ext}"
            dest_path = os.path.join(dest_dir, new_name)
            counter += 1
        final_name = os.path.basename(dest_path)

        shutil.copy(local_path, dest_path)
        size_mb = os.path.getsize(local_path) / (1024 * 1024)
        upload_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if counter > 1:
            log(f"File name exists, renamed to: {final_name}", "WARNING")

        print_file_summary(
            i, len(file_list), final_name, size_mb, dest_path, upload_time
        )

    elapsed = time.time() - start_time
    minutes, seconds = divmod(elapsed, 60)
    log(
        f"All files uploaded successfully\nTotal time: {int(minutes)}m {int(seconds)}s",
        "SUCCESS",
    )


# ✅ Run Upload
check_drive()
file_list, upload_dir = get_file_list(input_path)
ensure_target_folder(drive_target_folder)
upload_files(file_list, upload_dir, drive_target_folder)
