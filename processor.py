import os, re

image_dir = 'images'

for root, dirs, files in os.walk(image_dir):
    for f in files:
        if (os.path.splitext(f)[1].strip() != '.jpg'): continue
        out = os.popen('identify -format "%[fx:w] by %[fx:h] pixels" ' + os.path.join(root, f))
        out = out.readline().strip()

        m = re.search('(^\d{1,4}) by (\d{1,4}) pixels$', out)
        
        if not m:
            print 'no match for', f
            continue

        dims = tuple([m.group(1), m.group(2)])
        
        if (dims[0] > dims[1]):
            print 'landscape'
        else:
            print 'portrait'
