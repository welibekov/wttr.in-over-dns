# Get weather report through...OMG, through DNS.
If you are in place, where dns is only allowed traffic,you can still get weather report.
  

**To get report through A record:**    
```bash
# Linux 
dig @NS_IPADDRESS nuremberg.example.com A +short | tr '\n' '.' | xargs -I@ python -c "import sys;print ''.join([chr(int(i)) for i in sys.argv[1].split('.')[:-1]])" @

# MacOS X
dig @NS_IPADDRESS nuremberg.example.com A +short | tr '\n' '.' | xargs -I@ python -c "import sys;print ''.join([chr(int(i)) for i in sys.argv[1].split('.')[:-1]])" @
```

**To get report through TXT record:**    
```bash
# Linux
dig @NS_IPADDRESS nuremberg.example.com TXT +short | base64 -i --decode

# MacOS X
dig @NS_IPADDRESS nuremberg.example.com TXT +short | tr -d '"' | base64 -D
```

**To get report through SRV record:**
```bash
# Linux
dig @NS_IPADDRESS nuremberg.example.com SRV +short | awk '{"echo "$4" | base64 -i --decode"|getline $4;printf "%s\nTemp %s C\nWind %s-%s km/h\n",$4,$1,$2,$3}'

# MacOS X
dig @NS_IPADDRESS nuremberg.example.com SRV +short | awk '{"echo "$4" | tr -d '.' | base64 -D"|getline $4;printf "%s\nTemp %s C\nWind %s-%s km/h\n",$4,$1,$2,$3}'
```

Here is simple zonefile config:  
```json
{
    "example.com": {
        "ns":
            {
                "record": "ns1.example.com",
                "ttl": "600"
            },
        "a":
            {
                "ttl": "600",
                "record": "ns1.example.com",
                "ip": "1.1.1.1"
            }
      }
}
```

**Some weatherdns options:**  
```bash
-p PORT == bind port, default is 53
-s HOST == bind host, default is 0.0.0.0
-f FILE == pass to zone file, mandatory option
-h HELP == call help
```
