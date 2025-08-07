import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import io
from googleapiclient.http import MediaIoBaseDownload
import boto3
from botocore.exceptions import ClientError
import json 
from google.oauth2 import service_account
from datetime import datetime

# Global clients for efficiency - created once, reused across invocations
s3_client = boto3.client('s3')
secrets_client = boto3.client('secretsmanager')

# Configuration constants
BUCKET_NAME = "healthcare-data-lake-dea-2025"
STATE_KEY = "state/last_run_state.json"

def get_google_credentials():
    """Retrieve Google service account credentials from AWS Secrets Manager"""
    secret_value = secrets_client.get_secret_value(SecretId='healthcare-pipeline-google-creds')
    return json.loads(secret_value['SecretString'])

def load_state_file():
    """Load pipeline state from S3, return default if doesn't exist"""
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=STATE_KEY)
        file_content = response['Body'].read().decode('utf-8')
        return json.loads(file_content)
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            print("State file not found - first run, using default state")
            return {"last_pipeline_run": None, "files": {}}
        else:
            print(f"S3 error loading state file: {e}")
            raise e

def save_state_file(state_data):
    """Save pipeline state to S3"""
    try:
        state_json = json.dumps(state_data, indent=2)
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=STATE_KEY,
            Body=state_json,
            ContentType='application/json'
        )
        print(f"State file saved to s3://{BUCKET_NAME}/{STATE_KEY}")
        return True
    except ClientError as e:
        print(f"Error saving state file: {e}")
        raise e

def should_process_file(file_info, state_data):
    """Check if file needs processing based on modified time"""
    filename = file_info.get('name')
    drive_modified_time = file_info.get('modifiedTime')
    
    # If file not in state, process it (new file)
    if filename not in state_data['files']:
        print(f"New file detected: {filename}")
        return True
    
    # Compare modified times (ISO strings can be compared directly)
    last_processed_time = state_data['files'][filename].get('last_processed')
    if not last_processed_time or drive_modified_time > last_processed_time:
        print(f"File changed: {filename} (Drive: {drive_modified_time}, Last: {last_processed_time})")
        return True
    
    print(f"File unchanged, skipping: {filename}")
    return False

def update_file_state(state_data, file_info, current_time):
    """Update state for successfully processed file"""
    filename = file_info.get('name')
    state_data['files'][filename] = {
        'file_id': file_info.get('id'),
        'last_modified_in_drive': file_info.get('modifiedTime'),
        'last_processed': current_time
    }

def search_file():
    """Search file in drive location"""
    google_creds_json = get_google_credentials()
    creds = service_account.Credentials.from_service_account_info(google_creds_json)
    
    try:
        service = build("drive", "v3", credentials=creds)
        files = []
        page_token = None
        while True:
            response = (
                service.files()
                .list(
                    q="'1gtoGpmQetKmrGcy3Yo1zrE2Rf4CuY55e' in parents and mimeType='text/csv'",
                    spaces="drive",
                    fields="nextPageToken, files(id, name, mimeType, modifiedTime, createdTime)",
                    pageToken=page_token,
                )
                .execute()
            )
            for file in response.get("files", []):
                print(f'Found file: {file.get("name")}, Modified: {file.get("modifiedTime")}')
            files.extend(response.get("files", []))
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break
    except HttpError as error:
        print(f"An error occurred: {error}")
        files = None
    return files

def download_file(file_id, filename):
    """Downloads a file from Google Drive"""
    google_creds_json = get_google_credentials()
    creds = service_account.Credentials.from_service_account_info(google_creds_json)

    try:
        service = build("drive", "v3", credentials=creds)
        request = service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%")

        print(f"Successfully downloaded {filename}")
        return file.getvalue()
    except HttpError as error:
        print(f"An error occurred downloading {filename}: {error}")
        return None

def upload_to_s3(file_data, filename, s3_key):
    """Upload file data to S3 using global client"""
    try:
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=file_data
        )
        print(f"Successfully uploaded {filename} to s3://{BUCKET_NAME}/{s3_key}")
        return True             
    except ClientError as e:
        print(f"Error uploading {filename}: {e}")
        return False

def process_all_files():
    """Download only changed CSV files from Google Drive with state management"""
    current_time = datetime.utcnow().isoformat() + 'Z'  # ISO format timestamp
    
    try:
        print("=== PIPELINE START ===")
        
        # Step 1: Load existing state (ONE S3 call)
        print("Loading pipeline state...")
        state = load_state_file()
        print(f"Previous run: {state.get('last_pipeline_run', 'Never')}")
        
        # Step 2: Get all files from Google Drive
        print("Searching for files in Google Drive...")
        file_list = search_file()
        
        if not file_list:
            print("No files found!")
            return []
        
        print(f"Found {len(file_list)} total files in Google Drive")
        
        # Step 3: Process only changed files
        successful_downloads = []
        failed_count = 0
        skipped_count = 0
        
        for file_info in file_list:
            file_id = file_info.get('id')
            filename = file_info.get('name')
            
            # Check if file needs processing using state
            if should_process_file(file_info, state):
                print(f"\n🔄 Processing: {filename}")
                downloaded_data = download_file(file_id, filename)
                
                if downloaded_data:
                    s3_key = f"data/{filename}"
                    if upload_to_s3(downloaded_data, filename, s3_key):
                        successful_downloads.append({
                            'file_id': file_id,
                            'filename': filename,
                            'data': downloaded_data
                        })
                        # Update state for successfully processed file
                        update_file_state(state, file_info, current_time)
                    else:
                        failed_count += 1
                else:
                    failed_count += 1
            else:
                skipped_count += 1
        
        # Step 4: Update pipeline run timestamp and save state (ONE S3 call)
        state['last_pipeline_run'] = current_time
        save_state_file(state)
        
        print(f"\n=== PIPELINE SUMMARY ===")
        print(f"Processed: {len(successful_downloads)} files")
        print(f"Skipped (unchanged): {skipped_count} files") 
        print(f"Failed: {failed_count} files")
        print(f"Efficiency: {skipped_count}/{len(file_list)} files skipped")
        
        return successful_downloads
        
    except Exception as e:
        print(f"Error in process_all_files: {e}")
        return []

def lambda_handler(event, context):
    """Main Lambda handler with state management"""
    try:
        # Process files with incremental logic
        result = process_all_files()
        
        if not result:
            return {
                'statusCode': 200,
                'body': 'No files needed processing (all up to date)'
            }
        
        return {
            'statusCode': 200,
            'body': f'Successfully processed {len(result)} changed files'
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Pipeline failed: {str(e)}'
        }
