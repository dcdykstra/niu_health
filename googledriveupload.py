"""
Uploads files to Google Drive
"""
import os.path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError, UnacceptableMimeTypeError, MediaUploadSizeError
from googleapiclient.http import MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials
from configlog import config, logger

def get_drive_service():
    """Creates the Google Drive Service to Upload files"""
    scope = ["https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
                os.path.join(config.currentpath, 'service_account.json'), scopes=scope)
    return build('drive', 'v3', credentials=credentials)

def upload_xlsx(excel_file_name, excel_file_path):
    """Uploads Excel File to Shared Folder from Config"""
    file_metadata = {
        'name': excel_file_name,
        'mimeType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'parents': [config.drivefolderid]}
    media = MediaFileUpload(excel_file_path,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    try:
        service = get_drive_service()
        file_upload = service.files().create(
            body=file_metadata, media_body=media, supportsAllDrives=True).execute()

    except (HttpError, UnacceptableMimeTypeError, MediaUploadSizeError) as error:
        error_msg = f"failed to upload {error}"
        print(error_msg)
        logger.error(error_msg)
        file_upload = None

    return file_upload.get('id')
