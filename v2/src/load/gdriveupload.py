from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from src.config.configlog import config, logger


def upload_files(files: list):
    gauth = GoogleAuth()
    drive = GoogleDrive(gauth)

    for upload_file in files:
        name = upload_file.split("/")[-1]
        gfile = drive.CreateFile(
            {
                "title": name,
                "parents": [
                    {
                        "kind": "drive#fileLink",
                        "id": config.drivefolderid,
                    }
                ],
            }
        )  # Read file and set it as the content of this instance.
        gfile.SetContentFile(upload_file)
        gfile.Upload(param={"supportsTeamDrives": True})  # Upload the file.
