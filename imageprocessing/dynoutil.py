import boto
from boto import dynamodb
from boto.dynamodb import condition

table_name = 'family_photo'
dyno_key = 'dallasmarathon'

connDB = boto.connect_dynamodb()
table = connDB.get_table(table_name)

def getRecords():
    layer = dynamodb.layer2.Layer2()

    results = table.scan({'id':condition.EQ('dallasmarathon')})

    for result in results:
        item = boto.dynamodb.item.Item(
            table, 
            hash_key = result['id'],
            range_key = result['taken'],
            attrs = {
                'full' : result['full'],
                'thumb' : result['thumb'],
            })

        item.put_attribute('full', result['full'].replace('https', 'http'))
        item.put_attribute('thumb', result['thumb'].replace('https', 'http'))
        print item.save()

getRecords()