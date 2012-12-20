var express     = require('express');
var aws         = require('aws-sdk');
var config      = require('./config.js');

aws.config.update({accessKeyId: config.key, secretAccessKey: config.secret});
aws.config.update({region: 'us-east-1'});

var app = express();

app.configure(function(){
  var maxage = 1209600;
  app.set('views', __dirname + '/views');
  app.set('view engine', 'jade');
  app.use(express.static(__dirname + '/public', { maxAge : maxage }));
  app.use(app.router);
});

function createResponse(res, scanner) {
  var db = new aws.DynamoDB();

  db.client.scan(scanner, function(err, data) {
    render = {pageTitle : 'Dallas Marathon 2012'};
    console.log("Data");
    console.log(data);

    if (err) {
      console.log(err);
      render.msg = err.message;
    }
    else if (!data || data.Items.length == 0) 
      render.msg = 'no more images';
    else {
      render.lastitem = data.Items[data.Items.length - 1].taken.N;
      render.items = data.Items;
    }

    res.render('index.jade', render);
  });
}

function getScanner() {
  return { TableName : config.db, Limit : 20 };
}

function getHome(req, res) {  
  createResponse(res, getScanner());
}

function getSpecificImage(req, res) {
  console.log('Found id');
  var scanner = getScanner();

  scanner.ExclusiveStartKey = {
      HashKeyElement : { S : 'dallasmarathon' },
      RangeKeyElement : { N : req.params.id + '' },
      ComparisonOperator : 'GE'
  };

  createResponse(res, scanner);
}

app.get('/', getHome);
app.get('/:id', getSpecificImage);

var port = 8888;
app.listen(port);
console.log('Server running at http://127.0.0.1:' + port);