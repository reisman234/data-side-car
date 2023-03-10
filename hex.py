import sys
import binascii

argv = sys.argv
argc = len(argv)

if argc != 2:
    print('Usage: python hex.py [file_name]')
    quit()

with open(argv[1], 'rb') as f:
    while True:
        data = f.read(2048)
        if not data:
            break
        sys.stdout.write(binascii.hexlify(data).decode())
