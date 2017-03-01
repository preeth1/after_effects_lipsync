import os
import tempfile
import speech_recognition


class LipsyncGenerator:
    def __init__(self):
        pass

    def generate_timestamp_script_list(self):

        audio_file = 'hello_world.wav'
        # explicitly specified set of keywords
        keyword_entries = None
        audio_data_path, decoder = self._setup_decoder(audio_file, keyword_entries)

        raw_data = self._generate_raw_audio_data(audio_data_path)

        self._perform_speech_recognition(decoder, raw_data, keyword_entries)
        script_list = [(seg.word, seg.start_frame, seg.end_frame, decoder.lookup_word(seg.word))
                       for seg in decoder.seg()]
        line_to_print = ''
        for word in script_list:
            line_to_print = line_to_print + word[0] + ' '
        print('Words I heard: ', line_to_print)
        return script_list

    @staticmethod
    def _setup_decoder(audio_file, keyword_entries):

        language = "en-US"

        audio_file_type = audio_file.split(".")[1]

        if audio_file_type == 'wav':
            curr_dir = os.getcwd()
            data_dir = os.path.join(curr_dir, '../data/')
            speech_recognition_directory = '/Library/Python/2.7/site-packages/speech_recognition/'
            audio_data_path = os.path.join(data_dir, audio_file)
        else:
            raise speech_recognition.RequestError("file type must be .wav")

        assert isinstance(language, str), "``language`` must be a string"
        assert keyword_entries is None or all(
            isinstance(keyword, (type(""), type(u""))) and 0 <= sensitivity <= 1 for keyword, sensitivity in
            keyword_entries), "``keyword_entries`` must be ``None`` or a list of pairs of strings and numbers " \
                              "between 0 and 1"
        # import the PocketSphinx speech recognition module
        try:
            from pocketsphinx import pocketsphinx
        except ImportError:
            raise speech_recognition.RequestError(
                "missing PocketSphinx module: ensure that PocketSphinx is set up correctly.")
        except ValueError:
            raise speech_recognition.RequestError(
                "bad PocketSphinx installation detected; make sure you have PocketSphinx version 0.0.9 or better.")

        language_directory = os.path.join(os.path.dirname(speech_recognition_directory), "pocketsphinx-data", language)
        if not os.path.isdir(language_directory):
            raise speech_recognition.RequestError(
                "missing PocketSphinx language data directory: \"{}\"".format(language_directory))
        acoustic_parameters_directory = os.path.join(language_directory, "acoustic-model")
        if not os.path.isdir(acoustic_parameters_directory):
            raise speech_recognition.RequestError(
                "missing PocketSphinx language model parameters directory: \"{}\"".format(
                    acoustic_parameters_directory))
        language_model_file = os.path.join(language_directory, "language-model.lm.bin")
        if not os.path.isfile(language_model_file):
            raise speech_recognition.RequestError(
                "missing PocketSphinx language model file: \"{}\"".format(language_model_file))
        phoneme_dictionary_file = os.path.join(language_directory, "pronounciation-dictionary.dict")
        if not os.path.isfile(phoneme_dictionary_file):
            raise speech_recognition.RequestError(
                "missing PocketSphinx phoneme dictionary file: \"{}\"".format(phoneme_dictionary_file))

        # create decoder object
        config = pocketsphinx.Decoder.default_config()
        # set the path of the hidden Markov model (HMM) parameter files
        config.set_string("-hmm", acoustic_parameters_directory)
        config.set_string("-lm", language_model_file)
        config.set_string("-dict", phoneme_dictionary_file)
        # disable logging (logging causes unwanted output in terminal)
        config.set_string("-logfn", os.devnull)
        decoder = pocketsphinx.Decoder(config)

        return audio_data_path, decoder

    @staticmethod
    def _generate_raw_audio_data(audio_data_path):
        # obtain audio data
        r = speech_recognition.Recognizer()
        with speech_recognition.AudioFile(audio_data_path) as source:
            audio_data = r.record(source)
        # the included language models require audio to be 16-bit mono 16 kHz in little-endian format
        raw_data = audio_data.get_raw_data(convert_rate=16000, convert_width=2)
        return raw_data

    @staticmethod
    def _perform_speech_recognition(decoder, raw_data, keyword_entries):
        # obtain recognition results
        if keyword_entries is not None:
            with tempfile.NamedTemporaryFile("w") as f:
                # generate a keywords file - Sphinx documentation recommendeds sensitivities between 1e-50 and 1e-5
                f.writelines(
                    "{} /1e{}/\n".format(keyword, 100 * sensitivity - 110) for keyword, sensitivity in keyword_entries)
                f.flush()

                # perform the speech recognition with the keywords file (this is inside the context manager so the file
                # isn't deleted until we're done)
                decoder.set_kws("keywords", f.name)
                decoder.set_search("keywords")
                # begin utterance processing
                decoder.start_utt()
                # process audio data with recognition enabled (no_search = False), as a full utterance (full_utt = True)
                decoder.process_raw(raw_data, False, True)
                # stop utterance processing
                decoder.end_utt()
        # no keywords, perform freeform recognition
        else:
            # begin utterance processing
            decoder.start_utt()
            # process audio data with recognition enabled (no_search = False), as a full utterance (full_utt = True)
            decoder.process_raw(raw_data, False, True)
            # stop utterance processing
            decoder.end_utt()


if __name__ == "__main__":
    LipsyncGenerator().generate_timestamp_script_list()
