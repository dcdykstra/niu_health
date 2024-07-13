import os
from zipfile import ZipFile
from src.config.configlog import config


class FileCleaner:
    def __init__(self):
        pass

    def extract_zips(self, path):
        for item in os.listdir(path):
            if item.endswith(".zip"):
                file = os.path.join(path, item)
                with ZipFile(file, "r") as zip_ref:
                    zip_ref.extractall(path)

    def clear_zips(self, path):
        for item in os.listdir(path):
            if item.endswith(".zip"):
                os.remove(os.path.join(path, item))

    def rename_csv(self, new_name, report, path):
        for item in os.listdir(path):
            if item.endswith(".csv") and item.startswith(report):
                os.rename(os.path.join(path, item), os.path.join(path, new_name))

    def get_dir_path(self, dir):
        rel_path = os.path.join(config.outputdir, dir)
        return os.path.abspath(rel_path)

    def get_file(self, file_name, dir):
        return os.path.join(dir, file_name)


class DataCleaner:
    def __init__(self):
        pass

    def clean(self, df):
        df = df.dropna()
        df = df.drop_duplicates()
        return df
