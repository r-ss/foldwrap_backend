import glob
import os
import shutil
from hashlib import blake2b
import zipfile


class FileSystemUtils:
    def is_file_exist(path) -> bool:
        if os.path.isfile(path) or os.path.isdir(path):
            return True
        else:
            return False

    def check_dir(dir) -> None:
        if not os.path.isdir(dir):
            os.makedirs(dir)

    def delete_file(path) -> None:
        if os.path.isfile(path):
            os.remove(path)

    def remove_directory(dir) -> None:
        if os.path.isdir(dir):
            shutil.rmtree(dir)

    def delete_by_pattern(in_dir: str, pattern: str) -> None:
        """Example: FileSystemUtils.delete_by_pattern(config.UPLOADS_DIR_TEMP, "*.pdf")"""
        for path in glob.glob(in_dir + pattern):
            os.remove(path)

    def file_hash(path, digest_size) -> str:
        if os.path.isfile(path):
            h = blake2b(digest_size=digest_size)
            h.update(open(path, "rb").read())
            return h.hexdigest()

    def move_file(src, dst) -> None:
        shutil.move(src, dst)

    def get_filesize(path, kb=False) -> int:
        size = os.path.getsize(path)
        if kb:
            return round(size / 1024, 2)
        else:
            return size

    def list_visible_files(directory):
        visible_files = []
        for file in os.listdir(directory):
            if not file.startswith("."):
                visible_files.append(file)
        return visible_files

    def check_path_type(path):
        if os.path.isdir(path):
            return "directory"
        elif os.path.isfile(path):
            return "file"
        else:
            return "not found"

    def is_dir_empty(dir_path) -> bool:
        if os.path.exists(dir_path) and not os.path.isfile(dir_path):
            # Checking if the directory is empty or not
            if not os.listdir(dir_path):
                return True  # Empty directory
            else:
                return False  # Not empty directory
        # else:
        #     print("The path is either for a file or not valid")

    # def bytes_to_human_readable_size(num, suffix="b"):
    #     for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
    #         if abs(num) < 1024.0:
    #             return f"{num:3.1f}{unit}{suffix}"
    #         num /= 1024.0
    #     return f"{num:.1f}Yi{suffix}"

    def copy(src, dest, rewrite=False, ignore=False):
        if os.path.isdir(dest):
            if rewrite:
                shutil.rmtree(dest)

        try:
            if ignore:
                shutil.copytree(src, dest, ignore=shutil.ignore_patterns(".*", "*.fla"))
            else:
                shutil.copytree(src, dest)
        except OSError as e:
            # If the error was caused because the source wasn't a directory
            if e.errno == 20:
                shutil.copy(src, dest)
            else:
                raise Exception("Directory not copied. Error: %s" % e)

    def getHumanReadableFilesize(size, precision=2):
        suffixes = ["B", "KB", "MB", "GB", "TB"]
        suffixIndex = 0
        while size > 1024 and suffixIndex < 4:
            suffixIndex += 1  # increment the index of the suffix
            size = size / 1024.0  # apply the division
        return "%.*f%s" % (precision, size, suffixes[suffixIndex])

    def get_dir_size(start_path="."):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

    def make_zip(src, dest):
        if os.path.isfile(dest):
            os.remove(dest)
        shutil.make_archive(dest[:-4], "zip", src)

    def unzip(src, dest):
        if zipfile.is_zipfile(src):  # if it is a zipfile, extract it
            with zipfile.ZipFile(src) as item:  # treat the file as a zip
                item.extractall(dest)  # extract it in the specific directory
