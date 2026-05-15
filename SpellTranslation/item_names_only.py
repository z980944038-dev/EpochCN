import sys
with open(sys.argv[1], encoding='utf-8') as f:
    next(f)
    with open(sys.argv[2], 'w', encoding='utf-8', newline='\n') as out:
        for line in f:
            parts = line.rstrip('\n').rstrip('\r').split('\t')
            if parts and parts[0]:
                out.write(parts[0] + '\n')
