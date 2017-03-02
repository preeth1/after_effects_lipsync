import os
import json
import math
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

        script_data = [{"full_word": seg.word,
                        "start_time_s": float(seg.start_frame) / 100,
                        "end_time_s": float(seg.end_frame) / 100,
                        "phonemes": decoder.lookup_word(seg.word).split(" ")}
                       for seg in decoder.seg()]
        line_to_print = ''
        for word in script_data:
            line_to_print = line_to_print + word["full_word"] + ' '

        print('Words I heard: ', line_to_print)

        self.replace_phonemes_via_mapping(script_data)
        self.convert_times_to_frame_rates(script_data)
        output_filename = "test_file"
        self.write_phonemes_to_file(script_data, output_filename)

        dummy=5

    @staticmethod
    def replace_phonemes_via_mapping(script_data):

        # Read the info from the json file into the phoneme_mapping dictionary
        phoneme_mapping_json_path = os.path.join(os.getcwd() + "/../data", "phoneme_mapping.json")
        if not os.path.isfile(phoneme_mapping_json_path):
            raise ValueError("missing PocketSphinx phoneme dictionary file: \"{}\"".format(phoneme_mapping_json_path))

        with open(phoneme_mapping_json_path) as phoneme_mapping_json:
            phoneme_mapping = json.load(phoneme_mapping_json)

        for script_data_entry in script_data:
            script_data_entry["phonemes"] = [phoneme_mapping[phoneme] for phoneme in script_data_entry["phonemes"]]

    @staticmethod
    def convert_times_to_frame_rates(script_data):
        # frames per second
        frame_rate = 24.0
        one_frame_seconds = 1 / frame_rate
        for script_data_entry in script_data:
            script_data_entry["start_frame"] = math.ceil(script_data_entry["start_time_s"] / one_frame_seconds)
            script_data_entry["end_frame"] = math.ceil(script_data_entry["end_time_s"] / one_frame_seconds)

    @staticmethod
    def write_phonemes_to_file(script_data, output_filename):
        output_filepath = os.path.join(os.getcwd(), "../data" + output_filename + ".dat")
        if os.path.exists(output_filepath):
            # Write to that file
            file = open(output_filepath, 'r')
            dummy=4
        else:
            # Create and write to that file
            file = open(output_filepath, 'w')
            dummy=5


if __name__ == "__main__":
    LipsyncGenerator().generate_timestamp_script_list()
