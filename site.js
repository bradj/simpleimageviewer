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

function getHome(req, res) {  
  res.send('temp');
}

function getParams(route) {
  var params = { 
    TableName : config.db,
    HashKeyValue : { S : route.prefix },
    Limit : 20
  }

  if (route.id) {
    params.RangeKeyCondition = {
      AttributeValueList : [ { N : route.id + '' } ],
      ComparisonOperator : 'GE'
    }
  }

  return params;
}

function loadGallery(res, route) {
  var params = getParams(route);

  console.log('Request for ' + (route.id ? route.id : route.prefix));

  var db = new aws.DynamoDB();
  db.client.query(params, function(err, data) {
    var render = {pageTitle : route.title};

    if (err) {
      console.log(err);
      render.msg = err.message;
    }
    else if (!data || data.Count == 0)
      render.msg = 'no more images';
    else {
      render.lastitem = data.Items[data.Count - 1].taken.N;
      render.items = data.Items;
    }

    res.render('index.jade', render);
  });
}

function getSpecificHome(req, res) {
  var loc = req.params.loc;
  if (loc == null) res.send(404, 'not found');

  /*
  Routes for individual image galleries.
    ** prefix   - is used as the hash on Dynamo.
    ** title    - html title tag
  */
  var routes = {
    dallasmarathon : {
      prefix : 'dallasmarathon',
      title : 'Dallas Marathon 2012'
    },
    florida2012 : {
      prefix : 'florida2012',
      title : 'Florida Vacation 2012'
    }
  };

  // Make sure the prefix route passed in the url exists
  var route = routes[loc] ? routes[loc] : res.send(404, 'not found');
  // Append the id if it exists
  route.id = req.params.id ? req.params.id : null;
  loadGallery(res, route);
}

app.get('/', getHome);
app.get('/:loc', getSpecificHome);
app.get('/:loc/:id', getSpecificHome);

var port = 8888;
app.listen(port);
console.log('Server running at http://127.0.0.1:' + port);