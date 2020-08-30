import os
from os import listdir
from os.path import isfile, join
import capture_info as ci
import cmath
import math
import matplotlib.pyplot as plt
import numpy
import pickle
import sys
import wave, struct

global CAPTURE_PATH
CAPTURE_PATH = "./captures/"
PREPROCESSED_PATH = "./captures/preprocessed/"
OUTPUT_PATH = "./output/"

##  prompts the user to choose which file they wish to analyze.
def choose_file():
    myfiles = [f for f in listdir(CAPTURE_PATH) if isfile(join(CAPTURE_PATH, f))]
    numfiles = len(myfiles)
    filenum = 1
    for filename in myfiles:
        print("{}. {}".format(filenum,filename))
        filenum += 1
	
    no_val = True
    while(no_val):
        filechoice = input("Please enter the number of the file you would like to process: ")
        try:
            filechoice = int(filechoice)
            if(filechoice > 0 and filechoice <= numfiles):
                filechoice -= 1
                no_val = False
            else:
                raise ValueError
        except:
            print("Enter a number between 1 and {}.".format(numfiles))
    return myfiles[filechoice]

##  reads the binary file and returns the signal in complex form.
##  I have commented out the sections that save the data for quick reading later. I don't know
##      if anything like this really exists in python like it does MATLAB.
##  The flag is there to read the whole file or just part of the file. 0 is the whole file, > 0 is that percent of the file.
def read_file(filename,flag):
    shortfilename = filename.split('.')[0]
    mypath = CAPTURE_PATH+filename
    preprocessed = [f for f in listdir(PREPROCESSED_PATH)]
    #if(shortfilename in preprocessed):
    #    print("Loading in previously saved data...")
    #    # Getting back the objects:
    #    f=open(shortfilename+'.pkl','rb')
    #    signal = pickle.load(f)
    #    f.close()
    #    return signal

    print("Reading data...")
    signal = []
    num_iqpairs = os.path.getsize(mypath)//2
    if(flag != 0):
        num_iqpairs = int(num_iqpairs*float(flag))
    inputfile = os.open(mypath,os.O_RDONLY)
    for b in range(0,num_iqpairs):
        re_b = os.read(inputfile,1)
        im_b = os.read(inputfile,1)
        re = int.from_bytes(re_b,byteorder='big',signed=False)-127.5
        im = int.from_bytes(im_b,byteorder='big',signed=False)-127.5
        signal.append(complex(re,im))
    os.close(inputfile)
    
    # Saving the objects:
    #print("Saving the data for later...")
    #f= open(shortfilename+'.pkl', 'wb')
    #pickle.dump(signal, f, protocol=-1)
    #f.close()

    return signal

##  given a signal and its info (sample frequency,  plot it in the frequency or time domain.
##  if the flag is 0, plot in the time domain. If it is 1, plot in the frequency domain.
def plot(signal,signal_info, flag):
    if(flag == 0):
        timescale = []
        numsamples = len(signal)
        for i in range(0,numsamples):
            timescale.append(i*(1/signal_info.sample_rate))
        plt.plot(timescale,signal)
        plt.axis([0,signal_info.capture_period,min(signal),max(signal)])
        plt.show()
    else:
        signal_fft = numpy.fft.fft(signal)
        for i in range(0,len(signal_fft)):
            temp = 20*math.log10(abs(signal_fft[i]))
            signal_fft[i] = temp
        freqscale = []
        numsamples = len(signal_fft)
        step = signal_info.sample_rate/numsamples
        for i in range(0,numsamples):
            freqscale.append((-1*signal_info.sample_rate/2)+i*step)
        plt.plot(freqscale,signal_fft)
        plt.axis([(-1*signal_info.sample_rate/2),(signal_info.sample_rate/2),0,max(signal_fft)])
        plt.show()
    return

##  returns the phase error while wrapping around the -pi to pi discontinuity.
def wrap_subtract(phase1,phase2):
    if(abs(phase1-phase2) > math.pi):
        phaseerr = 2*math.pi - (abs(phase1) + abs(phase2))
        sign = int(phase2/abs(phase2))
        return sign*phaseerr
    else:
        return phase1-phase2

##  low pass filters and decimates the signal according to the factor.
##  the purpose of this is to tune out any other radio signals
def decimate(signal,signal_info,factor):
    # low pass filter the signal
    f_c = signal_info.sample_rate/(2*factor)
    sample_period = 1/signal_info.sample_rate
    numsamples = len(signal)
    lowpass = numpy.fft.fft(signal)
    freq_res = signal_info.sample_rate/numsamples

    #plot(signal,signal_info,1)

    # low pass filter at f_c
    for i in range(0,numsamples):
        freq = -1*(signal_info.sample_rate/2)+i*freq_res
        if(abs(freq)>f_c):
            lowpass[i]=complex(0,0.001)
    lowpass = numpy.fft.ifft(lowpass)

    #plot(lowpass,signal_info,1)

    decimated = []
    for i in range(0,numsamples,factor):
        decimated.append(lowpass[i])

    signal_info.sample_rate = signal_info.sample_rate/factor
    return (decimated,signal_info)


##  uses the PLL design to decode the FM signal. For more PLL theory see the main.html file.
##  assumes that the center frequency is the radio station that you want to listen in on.
def pll_decode(signal,signal_info):
    ## initialize variables
    f_c = signal_info.sample_rate/2
    sample_period = 1/signal_info.sample_rate
    num_samples = len(signal)
    signal.insert(0,0)
    decoded_signal = [complex(0,0)]
    vco_phase = 0

    ## decode
    for i in range(1,num_samples):
        ## phase detection
        #range of cmath.phase(*) is -pi to pi
        phase_err = wrap_subtract(cmath.phase(signal[i]),vco_phase)

        ## low-pass filter 
        alpha = (2*math.pi*f_c*sample_period)/(1+2*math.pi*f_c*sample_period)
        decoded_sample = alpha * phase_err + (1-alpha)*decoded_signal[i-1]
        decoded_signal.append(decoded_sample)

        ## change VCO phase
        vco_phase = vco_phase + cmath.phase(decoded_sample)

        ## wrap the VCO phase around the -pi to pi discontinuity. 
        if(vco_phase > math.pi):
            vco_phase = -2*math.pi + vco_phase
        if(vco_phase < math.pi):
            vco_phase = 2*math.pi + vco_phase 

    return decoded_signal

def write_wav(signal,signal_info):
    shortname = (signal_info.name).split('.')[0]
    f = wave.open(OUTPUT_PATH+shortname+'.wav','wb')
    f.setnchannels(1) #mono
    f.setsampwidth(2)
    f.setframerate(signal_info.sample_rate)
    for val in signal:
        value = int(abs(val))
        data = struct.pack('<h', value)
        f.writeframesraw(data)
    f.close()
    return

##  main function
if __name__ == "__main__":
    print("Usage: python3 process_fm.py [sample portion] [decimation factor]\n")
    filename = choose_file()
    if(len(sys.argv) > 1):
        signal = read_file(filename,sys.argv[1])
    else:
        signal = read_file(filename,0)
    signal_info = ci.fetch(filename)

    #plot(signal,signal_info,1) #take FFT and plot signal

    factor = 8
    if(len(sys.argv)>2):
        try:
            factor = int(sys.argv[2])
        except:
            factor = 8
    decimated,signal_info = decimate(signal,signal_info,factor)
    #this decimated signal focuses in on the radio station centered at 0 Hz

    #plot(decimated,signal_info,1)

    decoded = pll_decode(signal,signal_info)
    #this decodes the FM radio station, but it is still WFM

    #plot(decoded,signal_info,1)

    mono_channel,signal_info = decimate(decoded,signal_info,8)
    #this decimates again and brings the mono channel into focus

    #plot(mono_channel,signal_info,1)
    
    write_wav(mono_channel,signal_info)
    print("Your .wav file is ready to listen to!")
