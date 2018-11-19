# Traceroute Parser

Parse output of traceroute and visualize the path from source to destination

# Run
```
$ ./myTraceParser.py [destination]
```

Example:
```
$ ./myTraceParser.py google.com
```

![Example](https://github.com/trandinhkhoa/traceroute_parser/blob/master/example.png)

# TODO: 
- Store parsed results in file
- Find shortest path
- Scaling the distance between nodes in image with respect to the round trip time 
- Cover more cases (e.g. one hop does not always return data of all 3 probes, etc.)
