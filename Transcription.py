from datetime import timedelta

class Transcription:
    def __init__(self, text, start_time, end_time):
        assert type(text) == str
        assert type(start_time) == timedelta
        assert type(end_time) == timedelta
        self.text = text
        self.start_time = start_time
        self.end_time = end_time
    
    def get_text(self):
        return self.text

    def get_start_time(self):
        return self.start_time

    def get_end_time(self):
        return self.end_time
    
    def __str__(self):
        return "Transcription of the words " + self.text + ", starting at " + str(self.start_time) + " and ending at " + str(self.end_time)