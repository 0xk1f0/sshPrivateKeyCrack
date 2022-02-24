#!/usr/bin/python3
# Try to export public key from private key, which requires passphrase
# Cycle through wordlist until correct password is found

from subprocess import Popen, PIPE, DEVNULL
import sys
import multiprocessing as mp
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
    else:
        print("WARNING: Keyfile permissions could not be set/verified!")
        print("Always make sure the Keyfile has 'chmod 600' permissions!")

# wordlist handling
def load_wordlist():
    global wordlist_lines
    global wordlist_length
    wordlist = open(str(args.wordlist), 'rb')
    wordlist_lines = wordlist.readlines()
    wordlist_length = len(wordlist_lines)
    print(f"Loaded wordlist '{args.wordlist}', {wordlist_length} lines!")

# decrypt function
def exec_decrypt(word):
    process = Popen(["ssh-keygen", "-f", str(args.file), "-m", "pem", "-p", "-P", word], stdout=DEVNULL, stderr=PIPE, stdin=DEVNULL,)
    (out, err) = process.communicate()
    return err

# process function
def process_handler(word):
    while int(word.value) < int(wordlist_length):
        res = exec_decrypt(str(wordlist_lines[word.value].decode("utf-8")).strip())
        if not str(res).startswith("b'Failed"):
                print(">"+str(word.value)+"/"+str(wordlist_lines[word.value].decode("utf-8"))+"<")
                print("\nCRACKED:")
                print(str(args.file)+":"+str(wordlist_lines[word.value].decode("utf-8")))
                Popen(["mv", str(args.file), str(args.file)+".cracked"], stdout=DEVNULL, stderr=DEVNULL, stdin=DEVNULL,)
                sys.exit()
        print(str(word.value)+"/"+str(wordlist_lines[word.value].decode("utf-8")))
        word.value += 1

# main function
def main():
    load_wordlist()
    sleep(2)
    set_perm(args.file)
    sleep(2)
    manager = mp.Manager()
    cnt = manager.Value('i', 0)
    p1 = mp.Process(target=process_handler, args=(cnt,))
    p1.start()
    p2 = mp.Process(target=process_handler, args=(cnt,))
    p2.start()
    p1.join()
    p2.join()

# start here
if __name__ == "__main__":
    main()