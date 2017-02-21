#!/usr/bin/env python
import os

import sphinxbase as sb
import pocketsphinx as ps

MODELDIR = '/Library/Python/2.7/site-packages/pocketsphinx/model'
DATADIR = '/Users/preethi/Desktop'

this_dir = os.getcwd()

# Create a decoder with certain model
config = ps.Decoder.default_config()
config.set_string('-hmm', os.path.join(MODELDIR, 'en-us'))
config.set_string('-lm', os.path.join(MODELDIR, 'en-us.lm.bin'))
config.set_string('-dict', os.path.join(MODELDIR, 'cmudict-en-us.dict'))
decoder = ps.Decoder(config)

# Decode streaming data.
decoder.start_utt()
stream = open(os.path.join(DATADIR, 'TRLT.mp3'), 'rb')
while True:
    buf = stream.read(1024)
    if buf:
        decoder.process_raw(buf, False, False)
    else:
        break
decoder.end_utt()
stream.close()
print('Best hypothesis segments:', [seg.word for seg in decoder.seg()])
