from google.cloud import storage, speech
from config import misc
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file('config/gcp_credentials.json')

def upload_blob(bucket_name=misc.BUCKET_NAME, source_file_name=misc.LATEST_AUDIO_NAME, destination_blob_name=misc.DESTINATION_BLOB_NAME):
    '''Uploads a file to the bucket.'''


    storage_client = storage.Client(
        credentials=credentials
    )
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )


# given a GCS URI, return GCP's Speech-to-Text repsonse of the audio data at the URI
def get_gcs_transcription(gcs_uri="gs://" + misc.BUCKET_NAME + "/" + misc.DESTINATION_BLOB_NAME):
    '''Asynchronously transcribes the audio file specified by the gcs_uri.'''

    client = speech.SpeechClient(
        credentials=credentials
    )

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=44100,
        audio_channel_count=1,
        language_code="en-US",
        enable_word_time_offsets=True,
        model="video",
        
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    print("Waiting for operation to complete...")
    return operation.result(timeout=90)
        