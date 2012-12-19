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

function getImages(res) {
    var db = new aws.DynamoDB();
    db.client.scan({
        TableName : config.db,
        Limit : 50
    }, function(err, data) {
        if (err) { console.log(err); return; }

        res.render('index.jade', {
            pageTitle : 'Testing',
            items : data.Items
        });
    });
}

function displayImages(req, res) {
    getImages(res);
};

app.get('/', displayImages);

var port = 8888;
app.listen(port);
console.log('Server running at http://127.0.0.1:' + port);