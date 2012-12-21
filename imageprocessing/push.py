import os, re

from boto.exception import *
import boto
from boto import dynamodb
import time

table_name = 'family_photo'
dyno_key = 'dallasmarathon'
s3_folder = 'mommarathon/'
bucket_name = 'com.bradjanke.photos'
image_dir = 'images/output'

connDB = boto.connect_dynamodb()
table = connDB.get_table(table_name)
conns3 = boto.connect_s3()
b = conns3.create_bucket(bucket_name)

def createItem(obj, table):
    return table.new_item(
        hash_key  = obj['id'],
        range_key = obj['taken'],
        attrs     = {
            'thumb': obj['thumb'],
            'full' : obj['full']
        })

def addRecords(records):
    print 'adding records'
    items = []
    for f in records:
        if table.has_item(hash_key = f['id'], range_key = f['taken']):
            print 'Table has', f['id']
            continue
        items.append(createItem(f, table))

    batch = dynamodb.batch.BatchWriteList(dynamodb.layer2.Layer2())
    for not_used in range(1000):
        batch.add_batch(table, puts=items)
        unprocessed = batch.submit()
        if table_name not in unprocessed['UnprocessedItems']: break
        print 'Found unprocessed items', len(unprocessed['UnprocessedItems'][table_name])
        
        del items[:] # clear the list
        
        for item in unprocessed['UnprocessedItems'][table_name]:
            items.append(createItem(item['PutRequest']['Item'], table))

def getExif(f):
    out = os.popen('identify -format "%[EXIF:DateTime]" ' + f)
    out = out.readline().strip()
    m = re.search('^([0-9: ]+$)', out)

    if not m:
        print 'no datetime for', f
        return None
    return m.group(1)


collected = []
for key in b.list():
    key.make_public()
    m = re.search('(IMG_[0-9]{1,5}_full)', key.name)
    if not m: continue;

    f = os.path.join(image_dir, m.group(1) + '.jpg')
    epoch = time.mktime(time.strptime(getExif(f), "%Y:%m:%d %H:%M:%S"))
    full = key.generate_url(0, query_auth=False)
    
    collected.append({'id':dyno_key, 'taken':epoch, 'full':full, 'thumb':full.replace('_full', '_thumb')})

    if len(collected) >= 25:        
        addRecords(collected)
        del collected[:]