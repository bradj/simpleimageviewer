import os, re

image_dir = 'images'

for root, dirs, files in os.walk(image_dir):
    print 'in', root
    for f in files:
        f = os.path.join(root, f)
        split = os.path.splitext(f)

        if (split[1].strip() != '.jpg' or re.search('_thumb$', split[0])):
            print 'skipping thumb', f
            continue

        out = os.popen('identify -format "%[fx:w] by %[fx:h] pixels" ' + f)
        out = out.readline().strip()

        m = re.search('(^\d{1,4}) by (\d{1,4}) pixels$', out)
        
        if not m:
            print 'no match for', f
            continue

        dims = tuple([m.group(1), m.group(2)])        
        scale = '250' if dims[0] > dims[1] else 'x250'

        out = os.popen('convert %s -scale "%s" %s' % (f, scale, split[0] + '_thumb' + split[1]))
        print 'converted', f
