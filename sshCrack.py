#!/usr/bin/python3
# Try to export public key from private key, which requires passphrase
# Cycle through wordlist until correct password is found

from subprocess import Popen, PIPE, DEVNULL
import sys
import os
import multiprocessing as mp
from time import sleep
import argparse

# init option parser
parser = argparse.ArgumentParser(description="SSH Private-Key Passphrase Cracker")
parser.add_argument("-f", "--file", help = "Specify the path to the SSH Private-Key file", required=True)
parser.add_argument("-w", "--wordlist", help = "Specify the path to your Wordlist", required=True)
args = parser.parse_args()
cpuCount = int(os.cpu_count())

# permission checker
def set_perm(filepath):
    process = Popen(["chmod", "600", filepath], stdout=DEVNULL, stderr=PIPE, stdin=DEVNULL)
    (out, err) = process.communicate()
    if str(err) == "b''":
        print("Automatically changed keyfile permissions!")
        print(f"Starting with {cpuCount} processes...")
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
def process_handler(word,done):
    while int(word.value) < int(wordlist_length):
        targetWord = str(wordlist_lines[word.value].decode("utf-8")).strip()
        res = exec_decrypt(targetWord)
        if not str(res).startswith("b'Failed"):
            if done.value == "":
                done.value = targetWord
                end_all(done.value)
            else:
                return False
        print("X "+targetWord+" X")
        word.value += 1

# finisher function
def end_all(passwd):
    print("> "+passwd+" <")
    sleep(2)
    print("\nCRACKED:")
    print(str(args.file)+":"+passwd)
    Popen(["mv", str(args.file), str(args.file)+".cracked"], stdout=DEVNULL, stderr=DEVNULL, stdin=DEVNULL,)
    sys.exit()

# main function
def main():
    load_wordlist()
    sleep(2)
    set_perm(args.file)
    sleep(2)
    manager = mp.Manager()
    crackDone = manager.Value('s', "")
    cnt = manager.Value('i', 0)
    prcs = []
    for i in range(1,cpuCount):
        p = mp.Process(target=process_handler, args=(cnt,crackDone,))
        prcs.append(p)
        p.start()
    for i in prcs:
        i.join()

# start here
if __name__ == "__main__":
    main()