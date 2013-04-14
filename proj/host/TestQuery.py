#!/usr/bin/python
# Xiaohan Li
# Test the loadquery class

import LoadQuery
import sys
class TestQuery:
    if __name__ == '__main__':
        q = LoadQuery.LoadQuery()
        q.listen()
        while True:
            ch = sys.stdin.read(1)
            if ch != 'q':
                for server in q.balance:
                    print server, ', balance is:', q.balance[server]
            else:
                break;
        q.stop() 
        

