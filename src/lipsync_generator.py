import os
import json
from lipsync_generator_setup import LipsyncGeneratorSetup


class LipsyncGenerator:
    def __init__(self):
        pass

    def generate_timestamp_script_list(self):

        audio_file_name = 'hello_world.wav'

        # explicitly specified set of keywords
        keyword_entries = None

        audio_data_path, decoder = LipsyncGeneratorSetup.setup_decoder(audio_file_name, keyword_entries)

        raw_data = LipsyncGeneratorSetup.generate_raw_audio_data(audio_data_path)

        LipsyncGeneratorSetup.perform_speech_recognition(decoder, raw_data, keyword_entries)

        script_data = [(seg.word,
                        seg.start_frame,
                        seg.end_frame,
                        decoder.lookup_word(seg.word))
                       for seg in decoder.seg()]
        line_to_print = ''
        for word in script_data:
            line_to_print = line_to_print + word[0] + ' '

        print('Words I heard: ', line_to_print)

        self.replace_phonemes_via_mapping(script_data)

    def replace_phonemes_via_mapping(self, script_data):

        # Read the info from the json file into the phoneme_mapping dictionary
        phoneme_mapping_json_path = os.path.join(os.getcwd() + "/../data", "phoneme_mapping.json")
        if not os.path.isfile(phoneme_mapping_json_path):
            raise ValueError("missing PocketSphinx phoneme dictionary file: \"{}\"".format(phoneme_mapping_json_path))

        with open(phoneme_mapping_json_path) as phoneme_mapping_json:
            phoneme_mapping = json.load(phoneme_mapping_json)

        for script_data_entry in script_data:
            phoneme_list = script_data_entry[3].split(" ")
            phoneme_list = [phoneme_mapping[phoneme] for phoneme in phoneme_list]

            dummy=5



if __name__ == "__main__":
    LipsyncGenerator().generate_timestamp_script_list()
