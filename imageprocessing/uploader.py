import boto, os, re, uuid, time, hashlib
from boto.exception import *
from boto import dynamodb

bucket_name = 'com.bradjanke.photos'
image_dir = 'images/output'
dyno_key = 'dallasmarathon'

conns3 = boto.connect_s3()
b = conns3.create_bucket(bucket_name)

def uploadImage(image, key):
    try:
        print 'uploading', image

        k = b.new_key(key)
        k.set_contents_from_filename(image)
        k.set_acl('public-read')
        return k.generate_url(0, query_auth=False)
    except S3ResponseError, e:
        print e.error_code
        print e.error_message
    except Exception, e:
        print e
    return None

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

        full = uploadImage(f, dyno_key + fname)
        thumb = uploadImage(os.path.join(root, thumb), dyno_key + thumb)

        if (full == None or thumb == None):
            print 'full or thumb failed'