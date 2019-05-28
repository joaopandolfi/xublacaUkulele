#!/usr/bin/env python
"""
Xublaca Ukulele 
Afinador para Ukulele
"""

import pyaudio
from wave import struct as wave_struct
from numpy import blackman
from numpy.fft import rfft
from numpy import array
from numpy import log
import sys, time, os
import curses


CHUNK = 2048 # Chunk of audio input to consider
RATE = 44100 # Recording rate
WINDOW = blackman(CHUNK) # Using blackman window. For more information see 
                               # http://en.wikipedia.org/wiki/Window_function
SAMPLE_SIZE = 8 # Number of data points to average over. This is used for 2 things
                # 1. Reducing noise between subsequent string strokes
                # 2. We don't output too many values which might confuse the user


""" Platform independent non-blocking keyboard input. """
try: # Windows?
    import msvcrt
    def kbfunc():
        return ord(msvcrt.getch()) if msvcrt.kbhit() else 0
except: # Unix/Mac
    import select
    def kbfunc():
        inp, out, err = select.select([sys.stdin], [], [], 0.001) # 0.1 second delay
        return sys.stdin.readline() if sys.stdin in inp else 0

class UkeTuner:
    """ 
    This is the Ukulele Tuner class.

    +---------------------------------+
    | Ukulele |     String Number     |
    | Tuning  |  4  |  3  |  2  |  1  |
    +---------------------------------+
    |Standard | 392 | 262 | 330 | 440 |
    |         |  G  |  C  |  E  |  A  |
    +---------------------------------+
    |Baritone | 147 | 196 | 247 | 330 |
    |         |  D  |  G  |  B  |  A  |
    +---------------------------------+
    |D-Tuning | 440 | 294 | 370 | 494 |
    |         |  A  |  D  |  F# |  B  |
    +---------------------------------+
    |Low A    | 220 | 294 | 370 | 494 |
    |         |  A  |  D  |  F# |  B  |
    +---------------------------------+
    |Low G    | 196 | 262 | 330 | 440 |
    |         |  G  |  C  |  E  |  A  |
    +---------------------------------+
    """
    
    target_freq = 392
    # Frequency values have been taken from http://en.wikipedia.org/wiki/Note
    data = { 
        'G': (392, "4", "Primeira de cima"),
        'C': (262, "3", "Segunda de cima"),
        'E': (330, "2", "Segunda de baixo"),
        'A': (440, "1", "Primeira de baixo")
    }
    chords = ['G', 'C', 'E', 'A']
    tuneName = "Padrao"

    term_width = 80 # Stores the character width of the terminal
    
    def __init__(self):
        rows, columns = os.popen('stty size', 'r').read().split() # Get the terminal dimensions
        self.term_width = int(columns)
    
    def setTune(self,tune,tuneName):
        self.data = { 
            tune[0][0]: (tune[0][1], "4", "Primeira de cima"),
            tune[1][0]: (tune[1][1], "3", "Segunda de cima"),
            tune[2][0]: (tune[2][1], "2", "Segunda de baixo"),
            tune[3][0]: (tune[3][1], "1", "Primeira de baixo")
        }
        self.chords = chords = [tune[0][0], tune[1][0], tune[2][0], tune[3][0]]
        self.tuneName = tuneName

    def _print_header(self):
        lines = ["Xublaca Ukulele",
                "Afinacao-> "+self.tuneName,
                "Voce tem que alinhar o # com a marca |",
                "Aperte <Enter> para afinar a proxima corda"]
        print "=" * self.term_width
        for line in lines:
            ll = len(line) 
            spaces = (self.term_width - ll) / 2 # This computation is used to center the text
            print ' ' * spaces, line
        print "=" * self.term_width
        
    def _open_audio(self):
        """ Opens the audio device for listening """
        audio = pyaudio.PyAudio()
        stream = None
        while True: # Fix for Mac OS
            stream = audio.open(format = pyaudio.paInt16,
                                channels = 1,
                                rate = RATE,
                                input = True,
                                output = False, # TODO
                                frames_per_buffer = CHUNK)
            try:
                # On Mac OS, the first call to stream.read usually fails
                data = stream.read(CHUNK)
                break
            except:
                stream.close()
        self.audio = audio
        self.stream = stream

    def _switch_string(self, string):
        """ Sets the target frequency and tells the user to move to the next string """
        freq, string_num, help = self.data[string]
        print "\033[0m\Afinando em %s (corda %s) [%s]" % (string, string_num, help)
        self.target_freq = freq

    def _loop(self):
        """ This loop runs until the user hits the Enter key """
        last_n = [0] * SAMPLE_SIZE # Stores the values of the last N frequencies. 
                                   # This list is used as an array
        curpos = 0   # Stores the index to the array where we will store our next value
        last_avg = 1 # Stores the average of the last N set of samples.
                     # This value will be compared to the current average to detect 
                     # the change in note 
        # play stream and find the frequency of each chunk
        while True:
            perfect_cnt = 0
            data = self.stream.read(CHUNK)
            # unpack the data and times by the hamming window
            indata = array(wave_struct.unpack("%dh"%(len(data)/2), data))*WINDOW

            # Take the fft and square each value
            # FFT code thanks to Justin Peel
            fftData=abs(rfft(indata))**2
            # find the maximum
            which = fftData[1:].argmax() + 1
            # use quadratic interpolation around the max
            thefreq = 0
            if which != len(fftData)-1:
                y0,y1,y2 = log(fftData[which-1:which+2:])
                x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
                # find the frequency and output it
                thefreq = (which+x1)*RATE/CHUNK
            else:
                thefreq = which*RATE/CHUNK
            # Store this freq in an array
            last_n[curpos] = int(thefreq)
            curpos += 1
            if curpos == SAMPLE_SIZE:
                curpos = 0
            this_avg = sum(last_n) / SAMPLE_SIZE # Compute the average
            if (this_avg - last_avg) * 100 / last_avg > 2:
                last_avg = this_avg
                continue
            else:
                last_avg = this_avg
            variance = self.target_freq - this_avg
            self._plot(variance)

            if kbfunc() != 0: break # Go to the next note
            
    
    def _close_audio(self):
        """ Call this function at the end """
        self.stream.close()
        self.audio.terminate()
        
    def tune(self):
        """ Function to call """
        self._print_header()
        self._open_audio()
        for s in self.chords:
            self._switch_string(s)
            self._loop()
        self._close_audio()
        sys.stdout.write('\033[0m\n') # Reset colors
        sys.stdout.flush()
    
    def _plot(self, value):
        """ Prints a meter to help tune """
        negative = value > 0
        value = abs(int(value))
        center = self.term_width/2
        if value >= center: 
            value = center - 2

        line = ["."] * (self.term_width)
        line[0], line[center], line[-1] ='[', '|', ']'
        
        color = '\033[92m'
        if negative:
            line[center - value] = '#'
            if value > 1: color = '\033[93m'
        else:
            line[center + value] = '#'
            if value > 1: color = '\033[91m'

        sys.stdout.write('\r' + color + ''.join(line))
        sys.stdout.flush()
        
if __name__ == '__main__':
    baritone = [['D',147],['G',196],['B',247],['A',330]]
    dTuning =  [['A',440],['D',294],['F#',370],['B',494]]
    lowA =  [['A',220],['D',294],['F#',370],['B',494]]
    lowG =  [['G',196],['C',262],['E',330],['B',440]]

    u = UkeTuner()
    u.setTune(lowA, "A Baixo")
    u.tune()
