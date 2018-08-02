# Funny project, that allows you to get weather report through dns request.
If you are in place, where dns is only allowed traffic,you can still get weather report.
  

**To get report through A record:**    
 *dig @NS_IPADDRESS nuremberg.example.com A +short | tr '\n' '.' | xargs -I@ python -c "import sys;print ''.join([chr(int(i)) for i in sys.argv[1].split('.')[:-1]])" @*

**To get report through TXT record:**    
*dig @NS_IPADDRESS nurember.example.com TXT +short | base64 -i --decode*

**To get report through SRV record:**
*dig @localhost -p15353 nuremberg.example.com SRV +short|awk '{"echo "$4"|base64 -i --decode"|getline $4;printf "%s\nTemp %s C\nWind %s-%s km/h\n",$4,$1,$2,$3}'*

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
