#!/usr/bin/python
for c in range (1, 6):
    fname = "test" + str(c) + ".dat"
    file = open(fname, "wb")
    for i in range (1024 * 1024 * 10 * c):
        file.write("\xFF")
    file.close()
