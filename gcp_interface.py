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
def transcribe_gcs(author=None, gcs_uri="gs://" + misc.BUCKET_NAME + "/" + misc.DESTINATION_BLOB_NAME):
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
    response = operation.result(timeout=90)
    

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    raw_transcription = "{} Video too long to re-create. Transcript: ".format(author)

    transcriptions = []

    first_time = True
    prev = datetime.timedelta(0)
    for index, result in enumerate(response.results):
        words = result.alternatives[0].words
        # The first alternative is the most likely one for this portion.
        print("Confidence: {}".format(result.alternatives[0].confidence))
        raw_transcription += result.alternatives[0].transcript
        
        
        if index == len(response.results) - 1:
            transcriptions.append(Transcription(result.alternatives[0].transcript, prev, VIDEO_LENGTH))
        else:
            if prev == None:
                if len(words) != 0:
                    prev = words[0].start_time
                    transcriptions.append(
                        Transcription(
                        result.alternatives[0].transcript,
                        prev,
                        words[-1].end_time))
                else:
                    raise Exception("Mess.")
            else:
                transcriptions.append(
                    Transcription(
                        result.alternatives[0].transcript,
                        prev,
                        words[-1].end_time))
        if len(words) > 0:
            prev = words[-1].end_time
        else:
            if index == len(response.results) - 1:
                continue
            else:
                prev = None
    
    
    return response
    # return (transcriptions, raw_transcription)