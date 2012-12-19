import os, re

image_dir = 'images'
output_dir = 'images/output/'

for root, dirs, files in os.walk(image_dir):
    print 'in', root
    for fname in files:
        f = os.path.join(root, fname)
        split = os.path.splitext(f)

        if (split[1].strip() != '.jpg' or re.search('(_thumb|_full)$', split[0])):
            print 'skipping', f
            continue

        out = os.popen('identify -format "%[fx:w] by %[fx:h] pixels" ' + f)
        out = out.readline().strip()

        m = re.search('(^\d{1,4}) by (\d{1,4})', out)
        if not m:
            print 'no match for', f
            continue
        dims = tuple([m.group(1), m.group(2)])

        if not os.path.exists(output_dir): os.makedirs(output_dir)

        fname = os.path.splitext(fname)[0]
        path = os.path.normpath(output_dir + fname + '_thumb' + split[1])
        os.popen('convert %s -scale "%s" %s' % (f, 'x175', path))

        scale = '1800x1200' if dims[0] > dims[1] else '1200x1800'
        path = os.path.normpath(output_dir + fname + '_full' + split[1])
        os.popen('convert %s -scale "%s" %s' % (f, scale, path))

        print 'converted', fname