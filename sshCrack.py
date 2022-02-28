#!/usr/bin/python3
# How this script operates:
# 
# Currently, this script requires openssh to be installed.
# Using ssh-keygen, we try to extract the public-key from the private-key file 
# in ".pem" format, which requires the passphrase of the given key.
# Using the provided wordlist, we basically try out every password in it,
# until we do not get a failed attempt warning.
# We then mark the key with the file ending ".cracked".
# If we use the ssh-keygen conversion command again on a ".cracked" file,
# we are able to directly set our new passphrase.
#
# ssh-keygen will only accept the given key file, if permissions are
# correctly set. That's why the script also tries to "chmod 600" the file
# before proceeding with the cracking process.

from subprocess import Popen, PIPE, DEVNULL
from sys import exit as sysexit
from os import cpu_count
from multiprocessing import Process, Manager
from time import sleep
from argparse import ArgumentParser

parser = ArgumentParser(description="SSH Private-Key Passphrase Cracker")
parser.add_argument("-v", "--verbose", action='store_true', help='Verbose output')
parser.add_argument("-f", "--file", help = "Specify the path to the SSH Private-Key file", required=True)
parser.add_argument("-w", "--wordlist", help = "Specify the path to your Wordlist", required=True)
args = parser.parse_args()
cpuCount = int(cpu_count())

def set_perm(filepath):
    process = Popen(["chmod", "600", filepath], stdout=DEVNULL, stderr=PIPE, stdin=DEVNULL)
    (out, err) = process.communicate()
    if err.decode("utf-8") == "":
        if args.verbose: print("Automatically changed keyfile permissions!")
        print(f"Starting with {cpuCount} processes...")
    else:
        print('WARNING: Keyfile permissions could not be set/verified!\n' \
        + 'Always make sure the Keyfile has "chmod 600" permissions!')

def exec_attempt(word):
    process = Popen(["ssh-keygen", "-f", str(args.file), "-m", "pem", "-p", "-P", word], stdout=DEVNULL, stderr=PIPE, stdin=DEVNULL,)
    (out, err) = process.communicate()
    return err

def load_wordlist():
    global wordlist_lines
    global wordlist_length
    wordlist = open(str(args.wordlist), 'rb')
    wordlist_lines = wordlist.readlines()
    wordlist_length = len(wordlist_lines)
    if args.verbose: print(f"Loaded wordlist '{args.wordlist}', {wordlist_length} lines!")

def process_handler(word,done):
    while int(word.value) < int(wordlist_length):
        targetWord = str(wordlist_lines[word.value].decode("utf-8")).strip()
        res = exec_attempt(targetWord)
        if not res.decode("utf-8").startswith("Failed"):
            if done.value == "":
                done.value = targetWord
                end_all(done.value)
            else:
                return False
        if args.verbose: print("✗ "+targetWord+"✗")
        word.value += 1

def end_all(passwd):
    print("✓ "+passwd+" ✓")
    sleep(2)
    print('\nCRACKED:\n' \
    + str(args.file)+":"+passwd)
    Popen(["mv", str(args.file), str(args.file)+".cracked"], stdout=DEVNULL, stderr=DEVNULL, stdin=DEVNULL,)
    sysexit()

def main():
    load_wordlist()
    set_perm(args.file)
    sleep(2)
    print("Working...\n")
    crackDone = Manager().Value('s', "")
    cnt = Manager().Value('i', 0)
    procs = []
    for i in range(1,cpuCount):
        p = Process(target=process_handler, args=(cnt,crackDone,))
        p.start()
        procs.append(p)
    for prc in procs:
        prc.join()

if __name__ == "__main__":
    main()