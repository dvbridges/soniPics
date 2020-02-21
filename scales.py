"""
Holds scales, midinotes and base midi note value.
"""

scales = {}
scales['Am'] = {'scale': ['A', 'B', 'C', 'D', 'E', 'F', 'G'], 'offset': 9}
scales['Bm'] = {'scale': ['B', 'C#', 'D', 'E', 'F#', 'G', 'A'], 'offset': 11}
scales['Cm'] = {'scale': ['C', 'D', 'D#', 'F', 'G', 'G#', 'A#'], 'offset': 0}
scales['Dm'] = {'scale': ['D', 'E', 'F', 'G', 'A', 'A#', 'C'], 'offset': 2}
scales['Em'] = {'scale': ['E', 'F#', 'G', 'A', 'B', 'C', 'D'], 'offset': 4}
scales['Fm'] = {'scale': ['F', 'G', 'G#', 'A#', 'C', 'C#', 'D#'], 'offset': 5}
scales['Gm'] = {'scale': ['G', 'A', 'A#', 'C', 'D', 'D#', 'F'], 'offset': 7}
scales['AM'] = {'scale': ['A', 'B', 'C#', 'D', 'E', 'F#', 'G#'], 'offset': 9}
scales['BM'] = {'scale': ['B', 'C#', 'D#', 'E', 'F#', 'G#', 'A#'], 'offset': 11}
scales['CM'] = {'scale': ['C', 'D', 'E', 'F', 'G', 'A', 'B'], 'offset': 0}
scales['DM'] = {'scale': ['D', 'E', 'F#', 'G', 'A', 'B', 'C#'], 'offset': 2}
scales['EM'] = {'scale': ['E', 'F#', 'G#', 'A', 'B', 'C#', 'D#'], 'offset': 4}
scales['FM'] = {'scale': ['F', 'G', 'A', 'A#', 'C', 'D', 'E'], 'offset': 5}
scales['GM'] = {'scale': ['G', 'A', 'B', 'C', 'D', 'E', 'F#'], 'offset': 7}
scales['GM1'] = {'scale': ['G', 'A', 'B', 'C', 'D', 'E', 'F#'], 'offset': 7}
scales['GM2'] = {'scale': ['G', 'A', 'B', 'C', 'D', 'E', 'F#'], 'offset': 7}

BASE_NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

BASE_MIDI_NOTE = 48


