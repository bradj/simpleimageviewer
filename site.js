var express     = require('express');
var aws         = require('aws-sdk');
var config      = require('./config.js');

aws.config.update({accessKeyId: config.key, secretAccessKey: config.secret});
aws.config.update({region: 'us-east-1'});

var app = express();

app.configure(function(){
  app.set('views', __dirname + '/views');
  app.set('view engine', 'jade');
  app.use(express.static(__dirname + '/public'));
  app.use(app.router);
});

function getImages(req, res) {
    var db = new aws.DynamoDB();

    scanner = {
      TableName : config.db,
      Limit : 25
    };

    if (req.params.id) {
      console.log('Found id');
      // scanner.ScanFilter = {
      scanner.ExclusiveStartKey = {
          HashKeyElement : { S : 'dallasmarathon' },
          RangeKeyElement : { N : req.params.id + '' },
          ComparisonOperator : 'EQ'
      };
    }

    db.client.scan(scanner, function(err, data) {
      render = {pageTitle : 'Testing'};
      console.log(data);

      if (err) console.log(err);
      else {
        render.lastitem = data.Items[data.Items.length - 1].taken.N;
        render.items = data.Items;
      }

      res.render('index.jade', render);
    });
}

function displayImages(req, res) {
    getImages(req, res);
};

app.get('/', displayImages);
app.get('/:id', displayImages);

var port = 8888;
app.listen(port);
console.log('Server running at http://127.0.0.1:' + port);