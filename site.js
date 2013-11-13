var express     = require('express');
var config      = require('./config.js');
var dynamo      = require('./dynamo.js');
var http     = require('http');

var app = express();

var cache = {};

app.configure(function(){
  var maxage = 1209600;
  app.set('views', __dirname + '/views');
  app.set('view engine', 'jade');
  app.use(express.static(__dirname + '/public', { maxAge : maxage }));
  app.use(app.router);
});

function getHome(req, res) {
  var items = [];
  for (var ii in config.routes)
    items.push(config.routes[ii])

  res.render('index.jade', {items:items, title:config.title});
  res.end();
}

function loadGallery(route, callback) {
  var params = dynamo.getParams(route);

  dynamo.getImages(params, function(data, msg) {
    var render = {
      pageTitle : route.title,
      shownext : true,
      showprevious : false
    };

    if (data) {
      render.lastitem = '/' + route.prefix + '/' + data.Items[data.Count - 1].taken.N;
      render.items = data.Items;
      render.shownext = data.Count >= config.galleryLimit;
      render.showprevious = route.id != null;
    }
    else
      render.msg = msg;

    callback(render, render.items != null ? render.items : null);
  });
}

function getGallery(req, res) {
  var loc = req.params.loc;
  var d = new Date();
  console.log(loc + ' requested');
  console.log('Request at ' + d.toLocaleString());
  
  // Make sure the prefix route passed in the url exists
  if (loc == null || !config.routes[loc]) {
    res.send(404, 'not found');
    return;
  }

  var route = config.routes[loc];

  // Append the id if it exists
  route.id = req.params.id ? req.params.id : null;

  loadGallery(route, function(render){
    res.render('gallery.jade', render);
    res.end();
  });
}

function getImage(req, res) {
  var loc = req.params.loc;
  var id = req.params.id;

  if (loc == null) { 
    res.send(404, 'not found');
    res.end();
    return;
  }

  dynamo.getImage({ prefix: loc, taken: id}, function(data, msg) {
    if (msg) {
      res.render('gallery.jade', {msg:msg});
      res.end();
      return;
    }

    var img = data.Items[0];
    http.get(img.full.S, function(response) {
      console.log(res);
      res.end();
    });
  });
}

app.get('/', getHome);
app.get('/:loc', getGallery);
app.get('/:loc/:id', getGallery);
app.get('/:loc/img/:id', getImage);

var port = config.port ? config.port : 8822;
app.listen(port);
console.log('Server running at http://127.0.0.1:' + port);