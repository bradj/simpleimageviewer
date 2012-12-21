import boto, os, re, uuid, time, hashlib, argparse
from boto.exception import *
from boto import dynamodb

def uploadFile(b, image, key, folder=None):
    try:
        if folder: key = '%s/%s' % (folder, key)

        k = b.new_key(key)
        k.set_metadata('Cache-Control', 'max-age=%d, public' % (86400 * 14))
        k.set_metadata('Content-Type', 'image/jpg')
        k.set_contents_from_filename(image)
        k.set_acl('public-read')
        print 'uploaded', image
    except S3ResponseError, e:
        print 'FAILED', image
        print e.error_code
        print e.error_message
    except Exception, e:
        print 'FAILED', image
        print e

def main():
    parser = argparse.ArgumentParser(prog='uploader.py')
    parser.add_argument(
        '-bucket',
        help='bucket to upload into',
        metavar='name.of.bucket',
        required=True)
    parser.add_argument(
        '-files', 
        help='directory of files to upload',
        metavar='/bar/dir',
        required=True)
    parser.add_argument(
        '-s3folder', 
        help='folder to place uploads into',
        required=False)

    args = parser.parse_args()
    bucket_name = args.bucket
    image_dir = os.path.normpath(args.files)
    dyno_key = args.s3folder

    conns3 = boto.connect_s3()
    b = conns3.create_bucket(bucket_name)

    for root, dirs, files in os.walk(image_dir):
        print 'in', root
        for fname in files:
            f = os.path.join(root, fname)
            split = os.path.splitext(f)

            if (split[1].strip() != '.jpg' or not re.search('(_full)$', split[0])):
                print 'skipping', fname
                continue

            thumb = fname.replace('_full', '_thumb')
            if not os.path.exists(os.path.join(root, thumb)):
                print 'thumb does not exist', thumb
                continue

            out = os.popen('identify -format "%[EXIF:DateTime]" ' + f)
            out = out.readline().strip()
            m = re.search('^([0-9: ]+$)', out)

            if not m:
                print 'no datetime for', f
                continue

            uploadFile(b, f, fname, dyno_key)
            uploadFile(b, os.path.join(root, thumb), thumb, dyno_key)

if __name__ == "__main__":
    main()