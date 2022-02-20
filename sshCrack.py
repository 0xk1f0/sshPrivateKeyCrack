# Try to export public key from private key, which requires passphrase
# Cycle through wordlist until correct password is found

from subprocess import Popen, PIPE, DEVNULL
import sys
from time import sleep

print("MAKE SURE THE KEYFILE HAS 'chmod 600' PERMISSIONS!")
sleep(1)
print("OPENSSH IS REQUIRED FOR THIS SCRIPT TO WORK!")
sleep(1)
print("PLEASE ONLY SPECIFY THE ABSOLUTE FILEPATH!")
sleep(2)

privateFile = input("Specify absolute Input-File Path: ")
wordlistFile = input("Specify absolute Wordlist Path: ")

def cmdline(word):
    process = Popen(["ssh-keygen", "-f", str(privateFile), "-m", "pem", "-p", "-P", word], stdout=DEVNULL, stderr=PIPE, stdin=DEVNULL,)
    (out, err) = process.communicate()
    return err

words = open(str(wordlistFile))

def main():
    count=0
    for w in words:
        res = cmdline(w.strip())
        if not str(res).startswith("b'Failed"):
                print("\nThe key is: "+w.strip())
                sys.exit()
        print(str(count)+"/"+str(w.strip()))
        count=count+1

main()