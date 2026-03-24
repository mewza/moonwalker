import re

with open('moonwalk_glsl.txt') as f:
    content = f.read()

def replacer(m):
    name_part = m.group(1)
    values = [v.strip() for v in m.group(2).split(',')]
    lines = []
    for i in range(0, len(values), 10):
        chunk = values[i:i+10]
        lines.append('    ' + ', '.join(chunk) + ',')
    lines[-1] = lines[-1].rstrip(',')
    return name_part + '\n' + '\n'.join(lines) + '\n);'

result = re.sub(r'(const float \w+\[\d+\] = float\[\]\()([^;]+)(\));', replacer, content, flags=re.DOTALL)

with open('moonwalk_glsl_formatted.glsl', 'w') as f:
    f.write(result)

print('Done!')
