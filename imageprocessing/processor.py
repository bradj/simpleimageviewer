import os, sys, re, argparse

image_dir = 'images'
output_dir = 'images/output/'


def main():
    parser = argparse.ArgumentParser(prog='processor.py')
    parser.add_argument(
        '-input',
        help='directory of images to be processed',
        metavar='/foo/dir',
        required=True)
    parser.add_argument(
        '-output', 
        help='output directory of processed images',
        metavar='/bar/dir',
        required=True)
    # parser.add_argument(
    #     '-w',
    #     help='width of scaled down image in pixels',
    #     metavar='integer',
    #     required=False)
    # parser.add_argument(
    #     '-h',
    #     help='height of scaled down image in pixels',
    #     metavar='integer',
    #     required=False)
    # parser.add_argument(
    #     '-q',
    #     help='quality of thumbnail image 0-100',
    #     metavar='0-100',
    #     required=False)

    args = parser.parse_args()
    image_dir = args.input
    output_dir = args.output

    try:
        image_dir = os.path.normpath(image_dir)
        output_dir = os.path.normpath(output_dir)
    except:
        print 'Paths failed to normalize. Make sure they are correct.'
        return

    if not os.path.exists(image_dir):
        print '%s does not exist' % image_dir
        return
    if not os.path.exists(output_dir):
        print '%s does not exist' % output_dir
        return

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
            path = os.path.join(output_dir, fname + '_thumb' + split[1])
            os.popen('convert %s -scale "%s" %s' % (f, 'x175', path))
            os.popen('jpegoptim --strip-all -m90 %s' % (path))

            scale = '1800x1200' if dims[0] > dims[1] else '1200x1800'
            path = os.path.join(output_dir, fname + '_full' + split[1])
            os.popen('convert %s -scale "%s" %s' % (f, scale, path))

            print 'converted', fname

if __name__ == "__main__":
    main()