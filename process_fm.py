from os import listdir
from os.path import isfile, join

CAPTURE_PATH = "./captures/"

def choose_file():
    myfiles = [f for f in listdir(CAPTURE_PATH) if isfile(join(CAPTURE_PATH, f))]
    numfiles = len(myfiles)
    filenum = 1
    for filename in myfiles:
        print("{}. {}".format(filenum,filename))
        filenum += 1
	
    no_val = True
    while(no_val):
        filechoice = input("Please enter the number of the file you would like to process:")
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

##  converts bytes type to int.
##  I should improve the robustness of this function
##  by allowing it to also accept signed and little endian input.
def byte2int(byte,signed=False,bigendian=True):
    byte = str(byte)
    print(byte)
    a= byte.index('x')+1
    b= len(byte)-1
    print(a)
    print(b)
    hex_data = byte[a:b]
    print(hex_data)
    return int(hex_data,16)


def read_file(filename):
    mypath = CAPTURE_PATH+filename
    signal = []
    with open(mypath,"rb") as inputfile:
        re = byte2int(inputfile.read(1))
        im = byte2int(inputfile.read(1))
        print("{} + {}j".format(re,im))
        raise ValueError
        re = int(re,16)-127.5
        im = int(im,16)-127.5
        signal.append(re+j*im)
    return signal


if __name__ == "__main__":
    filename = choose_file()
    signal = read_file(filename)
    print('success')
