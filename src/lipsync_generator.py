from lipsync_generator_setup import  LipsyncGeneratorSetup


class LipsyncGenerator:
    def __init__(self):
        pass

    def generate_timestamp_script_list(self):

        audio_file = 'hello_world.wav'
        # explicitly specified set of keywords
        keyword_entries = None
        audio_data_path, decoder = LipsyncGeneratorSetup._setup_decoder(audio_file, keyword_entries)

        raw_data = LipsyncGeneratorSetup._generate_raw_audio_data(audio_data_path)

        LipsyncGeneratorSetup._perform_speech_recognition(decoder, raw_data, keyword_entries)
        script_list = [(seg.word, seg.start_frame, seg.end_frame, decoder.lookup_word(seg.word))
                       for seg in decoder.seg()]
        line_to_print = ''
        for word in script_list:
            line_to_print = line_to_print + word[0] + ' '
        print('Words I heard: ', line_to_print)
        return script_list




if __name__ == "__main__":
    LipsyncGenerator().generate_timestamp_script_list()
