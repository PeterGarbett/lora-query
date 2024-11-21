#!/bin/bash -v

# Test various combinations 

./bin/python3 query.py 43b6e594 43b6d0a0
./bin/python3 query.py 6c72fe5c 43b6e594  
exit
./bin/python3 query.py 43b6e594 6c72fe5c
./bin/python3 query.py 433c1ce0 43b6d0a0
./bin/python3 query.py 6c72fe5c 433c1ce0 
./bin/python3 query.py  433c1ce0  6c72fe5c
./bin/python3 query.py  433c1ce0   43b6e594  

./bin/python3 query.py 6c72fe5c 43b6e594  

./bin/python3 query.py 6c72fe5c 43b6d0a0

./bin/python3 query.py 433c1ce0 6c72fe5c 
./bin/python3 query.py 433c1ce0 43b6e594  
  
./bin/python3 query.py 433c1ce0 43b6d0a0

#./bin/python3 query.py  43b6d0a0 43b6e594
#./bin/python3 query.py  43b6d0a0 6c72fe5c

 
