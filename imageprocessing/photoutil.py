import os, re

from boto.exception import *
import boto

local = 'images/output/thumbs'
s3_folder = 'mommarathon/'
bucket_name = 'com.bradjanke.photos'

conns3 = boto.connect_s3()
b = conns3.create_bucket(bucket_name)

def addMeta():
    for key in b.list():
        m = re.search('(IMG_[0-9]{1,5}_thumb.jpg)', key.name)
        if not m: continue
        meta = key.metadata
        meta.update({'Cache-Control' : 'max-age=%d, public' % (86400 * 14),
                     'Content-Type' : 'image/jpg'})
        key = key.copy(
            key.bucket.name,
            s3_folder + key.name,
            metadata = meta,
            preserve_acl = True)
        print key.name

def totalCompress():
    for root, dirs, files in os.walk('images/output/thumbs'):
        for f in files:
            p = os.popen('jpegoptim --strip-all -m90 %s' % (os.path.join(root, f)))
            print 'completed', f

def removeKeys():
    for key in b.list():
        m = re.search('(^mommarathon)', key.name)
        if not m:
            key.delete()
            print key.name

def reuploadImages():
    for key in b.list():
        m = re.search('(IMG_[0-9]{1,5}_thumb.jpg)', key.name)
        if not m: continue
        key.delete()

    for root, dirs, files in os.walk(local):
        for f in files:
            image = os.path.join(root, f)
            try:
                print 'uploading', image

                k = b.new_key(dyno_key + f)
                k.set_metadata('Cache-Control', 'max-age=%d, public' % (86400 * 14))
                k.set_metadata('Content-Type', 'image/jpg')
                k.set_contents_from_filename(image)
                k.set_acl('public-read')
            except S3ResponseError, e:
                print e.error_code
                print e.error_message
            except Exception, e:
                print e

removeKeys()