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
  res.render('index.jade');
}

function getParams(route) {
  var params = { 
    TableName : config.db,
    KeyConditions: {
      'id' : {
        AttributeValueList : [ { S : route.prefix } ],
        ComparisonOperator : 'EQ'
      }
    },
    Limit : 40
  };

  if (route.id) {
    params.KeyConditions['taken'] = {
      AttributeValueList : [ { N : route.id } ],
      ComparisonOperator : 'GT'
    };
  }

  return params;
}

function loadGallery(res, route) {
  var params = getParams(route);
  var reqlog = route.prefix;
  if (route.id) reqlog += ' ' + route.id;
  console.log('Request for ' + reqlog);

  var db = new aws.DynamoDB();
  db.client.query(params, function(err, data) {

    var render = {
      pageTitle : route.title,
      shownext : true,
      showprevious : false
    };

    if (err) {
      console.log(err);
      render.msg = err.message;
    }
    else if (!data || data.Count == 0)
      render.msg = 'no more images';
    else {
      render.lastitem = '/' + route.prefix + '/' + data.Items[data.Count - 1].taken.N;
      render.items = data.Items;
      if (data.Count < 40) render.shownext = false;
      if (route.id) render.showprevious = true;
    }

    res.render('gallery.jade', render);
  });
}

function getSpecificHome(req, res) {
  var loc = req.params.loc;
  var d = new Date();
  console.log(loc + ' requested');
  console.log('Request at ' + d.toLocaleString());
  
  if (loc == null) {
    res.send(404, 'not found');
    return;
  }

  var routes = config.routes;

  // Make sure the prefix route passed in the url exists
  if (!routes[loc]) {
    res.send(404, 'not found');
    return;
  }

  var rt = routes[loc];

  // Append the id if it exists
  rt.id = req.params.id ? req.params.id : null;
  loadGallery(res, rt);
}

app.get('/', getHome);
app.get('/:loc', getSpecificHome);
app.get('/:loc/:id', getSpecificHome);

var port = 8888;
app.listen(port);
console.log('Server running at http://127.0.0.1:' + port);