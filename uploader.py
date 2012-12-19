import boto, os, re, uuid, time, hashlib
from boto.exception import *
from boto import dynamodb

table_name = 'family_photo'
bucket_name = 'com.bradjanke.photos'
image_dir = 'images/test'
dyno_key = 'dallasmarathon'

conns3 = boto.connect_s3()
connDB = boto.connect_dynamodb()
b = conns3.create_bucket(bucket_name)
table = connDB.get_table(table_name)

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

def createItem(obj, table):
    return table.new_item(
        hash_key  = obj['id'],
        range_key = obj['taken'],
        attrs     = {
            'thumb': obj['thumb'],
            'full' : obj['full']
        })

def addRecord(records):
    items = []
    for f in records:
        if table.has_item(hash_key = f['id'], range_key = f['taken']):
            print 'Table has', f['id']
            continue
        items.append(createItem(f, table))

    for not_used in range(20):
        batch = dynamodb.batch.BatchWriteList(dynamodb.layer2.Layer2())
        batch.add_batch(table, puts=items)
        unprocessed = batch.submit()
        if table_name not in unprocessed['UnprocessedItems']: break
        
        del items[:] # clear the list

        for item in unprocessed['UnprocessedItems'][table_name]:
            items.append(createItem(item['PutRequest']['Item'], table))

for root, dirs, files in os.walk(image_dir):
    print 'in', root
    collected = []
    for fname in files:
        f = os.path.join(root, fname)
        split = os.path.splitext(f)

        if (split[1].strip() != '.jpg' or not re.search('(_full)$', split[0])):
            print 'skipping', fname
            continue

        thumb = f.replace('_full', '_thumb')
        if not os.path.exists(thumb):
            print 'thumb does not exist', thumb
            continue

        out = os.popen('identify -format "%[EXIF:DateTime]" ' + f)
        out = out.readline().strip()        
        m = re.search('^([0-9: ]+$)', out)

        if not m:
            print 'no datetime for', f
            continue

        epoch = time.mktime(time.strptime(m.group(1), "%Y:%m:%d %H:%M:%S"))
        full = uploadImage(f, dyno_key + str(time.time()))
        thumb = uploadImage(thumb, dyno_key + str(time.time()))

        if (full == None or thumb == None):
            print 'full or thumb failed'
            continue

        collected.append({'id':dyno_key, 'taken':epoch, 'full':full, 'thumb':thumb})

    if len(collected) > 0: addRecord(collected)