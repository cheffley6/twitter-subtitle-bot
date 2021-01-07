# Imports the Google Cloud client library
from google.cloud import storage


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    '''Uploads a file to the bucket.'''


    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )

bucket_name = "ulti-tweet-audio-bucket"
source_file_name = "listen_Speech_16k8b.flac"
destination_blob_name = "listen_Speech_16k8b"
upload_blob(bucket_name, source_file_name, destination_blob_name)