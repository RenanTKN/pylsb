from optparse import OptionParser
from PIL import Image
import string
import os

parser = OptionParser(description="Steganography with LSB")
parser.add_option("-i", "--image", dest="image", help="Input image")
parser.add_option("-w", "--write", dest="write",
                  help="Write the data on the image", action="store_true", default=False)
parser.add_option("-r", "--read", dest="read",
                  help="Read an image", action="store_true", default=False)
parser.add_option("-t", "--text", dest="text",
                  help="Text to be added on the image")
parser.add_option("-f", "--file", dest="file",
                  help="Text to be added on the image")
parser.add_option("-s", "--show", dest="show",
                  help="Show the generated image", action="store_true", default=False)
parser.add_option("-p", "--printable", dest="printable",
                  help="Outputs only printable chars", action="store_true", default=False)
(options, args) = parser.parse_args()


def textFitsInImage(binText, w, h):
    return len(binText) <= w * h * 3


def str2bin(text):
    return ''.join(format(ord(x), '08b') for x in text)


def int2bin(n):
    return "{0:08b}".format(n)


def handleChannel(channel, bit):
    return int(int2bin(channel)[:-len(bit)] + bit, 2)


def handlePixel(pixel, string):
    pixel = list(pixel)

    for i in range(3):
        if len(string) == 0:
            break
        else:
            pixel[i] = handleChannel(pixel[i], string[0])
            string = popString(string, 1)

    return tuple(pixel)


def getText():
    if options.text != None:
        return options.text
    else:
        if os.path.isfile(options.file):
            return open(options.file).read()
        else:
            raise Exception(f"File not found: {options.file}")


def popString(string, n):
    return string[n:] if len(string) > n else string[len(string):]


def writeLSB():
    string = binText

    for y in range(h):
        for x in range(w):

            px[x, y] = handlePixel(px[x, y], string)

            string = popString(string, 3)

            if len(string) == 0:
                return


def readLSB():
    binaryLSB = ""
    for y in range(h):
        for x in range(w):
            for i in px[x, y]:
                binaryLSB += int2bin(i)[-1:]

    output = ""
    for i in range(int(len(binaryLSB) / 8)):
        output += chr(int(binaryLSB[i * 8:i * 8 + 8], 2))

    return output


def validateOptions():
    if options.write == options.read:
        raise Exception(
            "The --read and --write can't be used together, you need to choose only one")

    if options.write:
        if options.text == None and options.file == None:
            raise Exception(
                "In write mode you need to enter a --text or a --file")
        if options.text != None and options.file != None:
            raise Exception("You cannot use --text and --file together")
        if image == None:
            raise Exception("Insert an image --image")


def saveImage(filename):
    image.save(filename)


def saveOutput(filename, content):
    if options.printable:
        printable = set(string.printable)
        content = "".join(filter(lambda x: x in printable, content))

    f = open(filename, "w")
    f.write(content)
    f.close()


text = ""
binText = ""
filename = ""
output = ""
imageFile = options.image
image = Image.open(imageFile)
px = image.load()
w, h = image.size


def main():
    global binText

    validateOptions()
    filename, extension = os.path.splitext(imageFile)

    if options.write:
        text = getText()
        binText = str2bin(text)
        newFileName = f"{filename}-lsb{extension}"

        if not textFitsInImage(binText, w, h):
            raise Exception("You need a bigger image, pixels not enough")

        writeLSB()

        if options.show:
            image.show()

        saveImage(newFileName)
        print(f"Image saved: {newFileName}")

    else:
        output = readLSB()
        newFileName = f"{filename}.txt"
        saveOutput(newFileName, output)
        print(f"File saved: {newFileName}")


if __name__ == "__main__":
    main()
