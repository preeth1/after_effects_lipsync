#!/usr/bin/env python
import os

import sphinxbase as sb
import pocketsphinx as ps

curr_dir = os.getcwd()
audio_file = 'hello_world.mp3'
model_dir = '/Library/Python/2.7/site-packages/pocketsphinx/model'
data_dir = os.path.join(curr_dir, '../data/')

# Create a decoder with certain model
config = ps.Decoder.default_config()
config.set_string('-hmm', os.path.join(model_dir, 'en-us'))
config.set_string('-lm', os.path.join(model_dir, 'en-us.lm.bin'))
config.set_string('-dict', os.path.join(model_dir, 'cmudict-en-us.dict'))
decoder = ps.Decoder(config)

# Decode streaming data.
decoder.start_utt()
a = os.path.join(data_dir, audio_file)
stream = open(os.path.join(data_dir, audio_file), 'rb')
while True:
    buf = stream.read(1024)
    if buf:
        decoder.process_raw(buf, False, False)
    else:
        break
decoder.end_utt()
stream.close()
print('Best hypothesis segments:', [seg.word for seg in decoder.seg()])


# Access N best decodings.
print ('Best 10 hypothesis: ')
for best, i in zip(decoder.nbest(), range(10)):
    print (best.hypstr, best.score)