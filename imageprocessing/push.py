import os, re, argparse

from boto.exception import *
import boto
from boto import dynamodb
import time

def createItem(obj, table):
    return table.new_item(
        hash_key  = obj['id'],
        range_key = obj['taken'],
        attrs     = {
            'thumb': obj['thumb'],
            'full' : obj['full']
        })

def addRecords(records, table):
    print 'adding records'
    items = []
    for f in records:
        if table.has_item(hash_key = f['id'], range_key = f['taken']):
            print 'Table has', f['full']
            continue
        items.append(createItem(f, table))

    if len(items) == 0: return

    batch = dynamodb.batch.BatchWriteList(dynamodb.layer2.Layer2())
    for not_used in range(1000):
        batch.add_batch(table, puts=items)
        print 'submitting batch'
        unprocessed = batch.submit()
        if table.name not in unprocessed['UnprocessedItems']: break
        print 'Found unprocessed items', len(unprocessed['UnprocessedItems'][table.name])
        
        del items[:] # clear the list
        
        for item in unprocessed['UnprocessedItems'][table.name]:
            items.append(createItem(item['PutRequest']['Item'], table))

def getExif(f):
    out = os.popen('identify -format "%[EXIF:DateTime]" ' + f)
    out = out.readline().strip()
    m = re.search('^([0-9: ]+$)', out)

    if not m:
        print 'no datetime for', f
        return None
    return m.group(1)

def main():
    parser = argparse.ArgumentParser(prog='push.py')
    parser.add_argument(
        '-t',
        help='dynamo table to push into',
        required=True)
    parser.add_argument(
        '-hash', 
        help='dynamo hash',
        required=True)
    parser.add_argument(
        '-b', 
        help='bucket to retrieve files from',
        required=True)
    parser.add_argument(
        '-images', 
        help='image directory to get exif data from',
        required=True)
    parser.add_argument(
        '-prefix', 
        help='S3 prefix to get items by',
        required=False)
    args = parser.parse_args()

    table_name = args.t
    dyno_key = args.hash
    prefix = args.prefix
    bucket_name = args.b
    image_dir = args.images

    connDB = boto.connect_dynamodb()
    table = connDB.get_table(table_name)
    conns3 = boto.connect_s3()
    b = conns3.create_bucket(bucket_name)
    print prefix

    collected = []
    for key in b.list(prefix=prefix):
        m = re.search('(IMG_[0-9]{1,5}(-[0-9]{1})?_full)', key.name)
        if not m: continue;

        f = os.path.join(image_dir, m.group(1) + '.jpg')
        if not os.path.exists(f): 
            print 'Could not find', f
            continue;
        epoch = time.mktime(time.strptime(getExif(f), "%Y:%m:%d %H:%M:%S"))
        full = key.generate_url(0, query_auth=False, force_http=True)
        
        collected.append({'id':dyno_key, 'taken':epoch, 'full':full, 'thumb':full.replace('_full', '_thumb')})

        if len(collected) >= 25:        
            addRecords(collected, table)
            del collected[:]

    if len(collected) > 0: addRecords(collected, table)

if __name__ == "__main__":
    main()