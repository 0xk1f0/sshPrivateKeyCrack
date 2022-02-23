#!/usr/bin/python3
# Try to export public key from private key, which requires passphrase
# Cycle through wordlist until correct password is found

from subprocess import Popen, PIPE, DEVNULL
import sys
from time import sleep
import argparse

# init option parser
parser = argparse.ArgumentParser(description="SSH Private-Key Passphrase Cracker")
parser.add_argument("-f", "--file", help = "Specify the absolute path to the SSH Private-Key file", required=True)
parser.add_argument("-w", "--wordlist", help = "Specify the absolute path to your Wordlist", required=True)
args = parser.parse_args()

# decrypt function
def exec_decrypt(word):
    process = Popen(["ssh-keygen", "-f", str(args.file), "-m", "pem", "-p", "-P", word], stdout=DEVNULL, stderr=PIPE, stdin=DEVNULL,)
    (out, err) = process.communicate()
    return err

# main function
def main():
    words = open(str(args.wordlist))
    count=0
    for w in words:
        res = exec_decrypt(w.strip())
        if not str(res).startswith("b'Failed"):
                print("\nThe key is: "+w.strip())
                sys.exit()
        print(str(count)+"/"+str(w.strip()))
        count=count+1

# start here
if __name__ == "__main__":
    print("MAKE SURE THE PRIVATE-KEY FILE HAS 'chmod 600' PERMISSIONS!")
    sleep(2)
    main()