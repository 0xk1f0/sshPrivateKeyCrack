#!/usr/bin/python3
# Try to export public key from private key, which requires passphrase
# Cycle through wordlist until correct password is found

from subprocess import Popen, PIPE, DEVNULL
import sys
from time import sleep
import argparse

# init option parser
parser = argparse.ArgumentParser(description="SSH Private-Key Passphrase Cracker")
parser.add_argument("-f", "--file", help = "Specify the path to the SSH Private-Key file", required=True)
parser.add_argument("-w", "--wordlist", help = "Specify the path to your Wordlist", required=True)
args = parser.parse_args()

# permission checker
def set_perm(filepath):
    process = Popen(["chmod", "600", filepath], stdout=DEVNULL, stderr=PIPE, stdin=DEVNULL)
    (out, err) = process.communicate()
    if str(err) == "b''":
        print("Automatically changed keyfile permissions!")
        print("Starting...")
        sleep(2)
    else:
        print("WARNING: Keyfile permissions could not be set/verified!")
        print("Always make sure the Keyfile has 'chmod 600' permissions!")
        sleep(2)

# decrypt function
def exec_decrypt(word):
    process = Popen(["ssh-keygen", "-f", str(args.file), "-m", "pem", "-p", "-P", word], stdout=DEVNULL, stderr=PIPE, stdin=DEVNULL,)
    (out, err) = process.communicate()
    return err

# main function
def main():
    words = open(str(args.wordlist))
    count=0
    set_perm(args.file)
    for w in words:
        res = exec_decrypt(w.strip())
        if not str(res).startswith("b'Failed"):
                print(">"+str(count)+"/"+str(w.strip()+"<"))
                print("\nCRACKED:")
                print(str(args.file)+":"+w.strip())
                Popen(["mv", str(args.file), str(args.file)+".cracked"], stdout=DEVNULL, stderr=DEVNULL, stdin=DEVNULL,)
                sys.exit()
        print(str(count)+"/"+str(w.strip()))
        count=count+1

# start here
if __name__ == "__main__":
    main()