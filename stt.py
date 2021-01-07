from google.cloud import storage
from google.cloud import speech


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

def transcribe_gcs(gcs_uri):
    '''Asynchronously transcribes the audio file specified by the gcs_uri.'''

    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    print("Waiting for operation to complete...")
    response = operation.result(timeout=90)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        print(u"Transcript: {}".format(result.alternatives[0].transcript))
        print("Confidence: {}".format(result.alternatives[0].confidence))


bucket_name = "ulti-tweet-audio-bucket"
source_file_name = "listen_Speech_16k8b.flac"
destination_blob_name = "listen_Speech_16k8b"
# upload_blob(bucket_name, source_file_name, destination_blob_name)

gcs_uri = "gs://" + bucket_name + "/" + destination_blob_name
transcribe_gcs(gcs_uri)