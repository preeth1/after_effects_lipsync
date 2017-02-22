import os
import tempfile
import speech_recognition

audio_file = 'hello_world.wav'

curr_dir = os.getcwd()
model_dir = '/Library/Python/2.7/site-packages/pocketsphinx/model'
data_dir = os.path.join(curr_dir, '../data/')
audio_data_path = os.path.join(data_dir, audio_file)

speech_recognition_directory = '/Library/Python/2.7/site-packages/speech_recognition/'

language = "en-US"
keyword_entries = None
#assert isinstance(audio_data_path, AudioData), "``audio_data_path`` must be audio data"
assert isinstance(language, str), "``language`` must be a string"
assert keyword_entries is None or all(
    isinstance(keyword, (type(""), type(u""))) and 0 <= sensitivity <= 1 for keyword, sensitivity in
    keyword_entries), "``keyword_entries`` must be ``None`` or a list of pairs of strings and numbers between 0 and 1"

# import the PocketSphinx speech recognition module
try:
    from pocketsphinx import pocketsphinx
except ImportError:
    raise speech_recognition.RequestError("missing PocketSphinx module: ensure that PocketSphinx is set up correctly.")
except ValueError:
    raise speech_recognition.RequestError(
        "bad PocketSphinx installation detected; make sure you have PocketSphinx version 0.0.9 or better.")

language_directory = os.path.join(os.path.dirname(speech_recognition_directory), "pocketsphinx-data", language)
if not os.path.isdir(language_directory):
    raise speech_recognition.RequestError("missing PocketSphinx language data directory: \"{}\"".format(language_directory))
acoustic_parameters_directory = os.path.join(language_directory, "acoustic-model")
if not os.path.isdir(acoustic_parameters_directory):
    raise speech_recognition.RequestError(
        "missing PocketSphinx language model parameters directory: \"{}\"".format(acoustic_parameters_directory))
language_model_file = os.path.join(language_directory, "language-model.lm.bin")
if not os.path.isfile(language_model_file):
    raise speech_recognition.RequestError("missing PocketSphinx language model file: \"{}\"".format(language_model_file))
phoneme_dictionary_file = os.path.join(language_directory, "pronounciation-dictionary.dict")
if not os.path.isfile(phoneme_dictionary_file):
    raise speech_recognition.RequestError("missing PocketSphinx phoneme dictionary file: \"{}\"".format(phoneme_dictionary_file))

# create decoder object
config = pocketsphinx.Decoder.default_config()
config.set_string("-hmm",
                  acoustic_parameters_directory)  # set the path of the hidden Markov model (HMM) parameter files
config.set_string("-lm", language_model_file)
config.set_string("-dict", phoneme_dictionary_file)
config.set_string("-logfn", os.devnull)  # disable logging (logging causes unwanted output in terminal)
decoder = pocketsphinx.Decoder(config)

# obtain audio data
r = speech_recognition.Recognizer()
with speech_recognition.AudioFile(audio_data_path) as source:
    audio_data = r.record(source)
raw_data = audio_data.get_raw_data(convert_rate=16000,
                                   convert_width=2)  # the included language models require audio to be 16-bit mono 16 kHz in little-endian format

# obtain recognition results
if keyword_entries is not None:  # explicitly specified set of keywords
    with tempfile.NamedTemporaryFile("w") as f:
        # generate a keywords file - Sphinx documentation recommendeds sensitivities between 1e-50 and 1e-5
        f.writelines("{} /1e{}/\n".format(keyword, 100 * sensitivity - 110) for keyword, sensitivity in keyword_entries)
        f.flush()

        # perform the speech recognition with the keywords file (this is inside the context manager so the file isn;t deleted until we're done)
        decoder.set_kws("keywords", f.name)
        decoder.set_search("keywords")
        decoder.start_utt()  # begin utterance processing
        decoder.process_raw(raw_data, False,
                            True)  # process audio data with recognition enabled (no_search = False), as a full utterance (full_utt = True)
        decoder.end_utt()  # stop utterance processing
else:  # no keywords, perform freeform recognition
    decoder.start_utt()  # begin utterance processing
    decoder.process_raw(raw_data, False,
                        True)  # process audio data with recognition enabled (no_search = False), as a full utterance (full_utt = True)
    decoder.end_utt()  # stop utterance processing

print('Best hypothesis segments:', [(seg.word, seg.start_frame, seg.end_frame) for seg in decoder.seg()])

# return results
hypothesis = decoder.hyp()
if hypothesis is not None:
    sr_hypothesis = hypothesis.hypstr
    print('Speech I recognized: ' + sr_hypothesis)
else:
    raise speech_recognition.UnknownValueError()  # no transcriptions available

