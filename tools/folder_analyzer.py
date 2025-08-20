# @title 📊 Folder Statistics Analyzer
folder_path = ""  # @param {type:"string"}

import os
import humanize
from datetime import datetime
import logging
from collections import Counter
from typing import List, Dict, Any

# Setup logging for Colab
logging.basicConfig(level=logging.INFO, format="%(message)s", force=True)
logger = logging.getLogger(__name__)


def create_ascii_bar(value: int, max_value: int, bar_length: int = 30) -> str:
    """
    Create ASCII bar chart for terminal display
    """
    if max_value == 0:
        return ""
    filled_length = int(round(bar_length * value / float(max_value)))
    return "█" * filled_length + "-" * (bar_length - filled_length)


def collect_file_data(folder_path: str) -> tuple:
    """
    Collect file data from the specified folder and its subfolders
    Returns: (file_data, total_size, file_count, dir_count)
    """
    file_data = []
    total_size = 0
    file_count = 0
    dir_count = 0

    for root, dirs, files in os.walk(folder_path):
        dir_count += len(dirs)
        for file in files:
            file_path = os.path.join(root, file)
            try:
                file_size = os.path.getsize(file_path)
                file_extension = os.path.splitext(file)[1].lower() or "no_extension"
                file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))

                file_data.append(
                    {
                        "name": file,
                        "path": file_path,
                        "size": file_size,
                        "extension": file_extension,
                        "modified": file_mod_time,
                        "parent_dir": os.path.basename(root),
                    }
                )

                total_size += file_size
                file_count += 1

            except (OSError, PermissionError) as e:
                logger.warning(f"⚠️  Cannot access: {file_path} - {e}")

    return file_data, total_size, file_count, dir_count


def display_basic_stats(file_count: int, dir_count: int, total_size: int) -> None:
    """Display basic folder statistics"""
    logger.info("\n📊 BASIC STATISTICS")
    logger.info("-" * 30)
    logger.info(f"📄 File count: {file_count:,}")
    logger.info(f"📁 Subfolder count: {dir_count:,}")
    logger.info(f"💾 Total size: {humanize.naturalsize(total_size)}")

    if file_count > 0:
        avg_size = total_size / file_count
        logger.info(f"📦 Average file size: {humanize.naturalsize(avg_size)}")


def display_largest_files(
    file_data: List[Dict[str, Any]], folder_path: str, top_n: int = 10
) -> None:
    """Display the largest files in the folder"""
    logger.info(f"\n🏆 TOP {top_n} LARGEST FILES")
    logger.info("-" * 50)

    if not file_data:
        logger.info("No files found")
        return

    largest_files = sorted(file_data, key=lambda x: x["size"], reverse=True)[:top_n]

    # Determine column width for proper alignment
    max_name_len = max(
        len(os.path.relpath(f["path"], folder_path)) for f in largest_files
    )

    for i, file in enumerate(largest_files, 1):
        rel_path = os.path.relpath(file["path"], folder_path)
        name_col = rel_path.ljust(max_name_len + 2)
        size_col = humanize.naturalsize(file["size"]).rjust(12)
        logger.info(f"{i:2d}. {name_col} ==> {size_col}")


def display_all_files(file_data: List[Dict[str, Any]]) -> None:
    """Display all files with their sizes"""
    logger.info("\n📄 ALL FILES & SIZES")
    logger.info("-" * 50)

    if not file_data:
        logger.info("No files found")
        return

    # Sort files alphabetically
    sorted_files = sorted(file_data, key=lambda x: x["name"].lower())

    # Determine column width for proper alignment
    max_name_len = max(len(f["name"]) for f in sorted_files)

    for i, file in enumerate(sorted_files, 1):
        name_col = file["name"].ljust(max_name_len + 2)
        size_col = humanize.naturalsize(file["size"]).rjust(12)
        logger.info(f"{i:3d}. {name_col} ==> {size_col}")


def display_size_distribution(file_data: List[Dict[str, Any]], file_count: int) -> None:
    """Display file size distribution"""
    logger.info("\n📈 FILE SIZE DISTRIBUTION")
    logger.info("-" * 40)

    if file_count == 0:
        logger.info("No files to analyze")
        return

    size_ranges = {
        "0-1KB": 0,
        "1KB-1MB": 0,
        "1MB-10MB": 0,
        "10MB-100MB": 0,
        "100MB-1GB": 0,
        ">1GB": 0,
    }

    for file in file_data:
        size_kb = file["size"] / 1024
        if size_kb < 1:
            size_ranges["0-1KB"] += 1
        elif size_kb < 1024:
            size_ranges["1KB-1MB"] += 1
        elif size_kb < 10240:
            size_ranges["1MB-10MB"] += 1
        elif size_kb < 102400:
            size_ranges["10MB-100MB"] += 1
        elif size_kb < 1048576:
            size_ranges["100MB-1GB"] += 1
        else:
            size_ranges[">1GB"] += 1

    max_range = max(size_ranges.values())
    for range_name, count in size_ranges.items():
        if count > 0:
            percentage = (count / file_count) * 100
            bar = create_ascii_bar(count, max_range)
            logger.info(
                f"{range_name:<12} | {bar} {count:>4} files ({percentage:.1f}%)"
            )


def display_extension_stats(file_data: List[Dict[str, Any]]) -> None:
    """Display file extension statistics"""
    logger.info("\n📝 FILE TYPE STATISTICS")
    logger.info("-" * 40)

    if not file_data:
        logger.info("No files to analyze")
        return

    extensions = [f["extension"] for f in file_data]
    ext_counter = Counter(extensions)

    if not ext_counter:
        logger.info("No file extensions found")
        return

    max_ext = max(ext_counter.values())

    # tampilkan semua extensions, urut berdasarkan jumlah (desc)
    for ext, count in ext_counter.most_common():
        ext_size = sum(f["size"] for f in file_data if f["extension"] == ext)
        bar = create_ascii_bar(count, max_ext)
        logger.info(
            f"{ext:<12} | {bar} {count:>4} files ({humanize.naturalsize(ext_size)})"
        )


def display_modification_stats(file_data: List[Dict[str, Any]]) -> None:
    """Display file modification statistics"""
    logger.info("\n⏰ FILE MODIFICATION STATISTICS")
    logger.info("-" * 40)

    if not file_data:
        logger.info("No files to analyze")
        return

    latest_file = max(file_data, key=lambda x: x["modified"])
    oldest_file = min(file_data, key=lambda x: x["modified"])

    logger.info(
        f"🆕 Newest: {latest_file['modified'].strftime('%Y-%m-%d %H:%M')} - {os.path.basename(latest_file['path'])}"
    )
    logger.info(
        f"🕰️ Oldest: {oldest_file['modified'].strftime('%Y-%m-%d %H:%M')} - {os.path.basename(oldest_file['path'])}"
    )


def analyze_folder(folder_path: str) -> None:
    """
    Analyze folder and display comprehensive statistics
    """
    if not os.path.exists(folder_path):
        logger.error(f"❌ Folder '{folder_path}' not found!")
        return

    if not os.path.isdir(folder_path):
        logger.error(f"❌ '{folder_path}' is not a folder!")
        return

    logger.info("📂 FOLDER ANALYSIS")
    logger.info("=" * 50)
    logger.info(f"📁 Path: {folder_path}")
    logger.info(f"⏰ Analysis time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 50)

    # Collect file data
    file_data, total_size, file_count, dir_count = collect_file_data(folder_path)

    # Display statistics
    display_basic_stats(file_count, dir_count, total_size)
    display_largest_files(file_data, folder_path)
    display_all_files(file_data)
    display_size_distribution(file_data, file_count)
    display_extension_stats(file_data)
    display_modification_stats(file_data)


# Run analysis
analyze_folder(folder_path)
