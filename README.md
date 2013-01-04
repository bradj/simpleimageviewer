Simple Image Viewer
====

What is this thing?
-------------------
Simple Image Viewer is a website that displays images.  It allows you to create galleries, put images into these galleries, and display them via a website.  There is no 'like' functionality or rating of any kind.  It literally just displays images.  What a novel concept.

Overview
--------
The images are uploaded to [Amazon S3](http://aws.amazon.com/s3/) via a Python script.  You have the option of running the images through a compressor before uploading them, however this step is optional.  Once the images have been uploaded they must be placed into a database, for this I use [DynamoDB](http://aws.amazon.com/dynamodb/).

Install
-------
1. Clone this repo
2. `npm install`
3. Install `imagemagick`
4. Install `jpegoptim`

## Upload Images
1. **Compress Images** - The images are compressed via [processor.py](https://github.com/bradj/simpleimageviewer/blob/master/imageprocessing/processor.py).
2. **Upload Images** - Upload the images via [uploader.py](https://github.com/bradj/simpleimageviewer/blob/master/imageprocessing/uploader.py).
3. **Push to Databse** - Create the database entries via [push.py](https://github.com/bradj/simpleimageviewer/blob/master/imageprocessing/push.py). 

## Configure Website
Now that you have all of your images in the cloud, you can configure the site to display them.

1. Copy **config.js.example** to **config.js**.
2. Replace the **aws.key** and **aws.secret** values with your secret and key.  To get these values [go here](http://aws.amazon.com/account/).
3. Replace **aws.db** value with the table name you would like to use for your photos.  I used **family_photos** for one of my sites.
4. Move to **Routes** below.

### Routes
Placing Routes in config.js is how your galleries are created.  Here is an example route:

```javascript
aws.routes = {
    familysite : {
      prefix : 'familysite',
      title : 'I am not in any of these pictures!'
    },
    mycat : {
      prefix : 'mycat',
      title : 'Forever Alone'
    }
};
```

// TODO : Go into more detail here.

#API/Tool References

1. http://www.imagemagick.org/script/command-line-tools.php
2. http://boto.cloudhackers.com/en/latest/index.html
3. http://docs.amazonwebservices.com/AWSJavaScriptSDK/latest/frames.html
4. https://github.com/aws/aws-sdk-js
5. http://expressjs.com/api.html
6. https://github.com/visionmedia/jade#readme
