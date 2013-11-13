var config      = require('./config.js');
var aws         = require('aws-sdk');

aws.config.update({accessKeyId: config.key, secretAccessKey: config.secret});
aws.config.update({region: 'us-east-1'});

exports.getParams = function (route) {
  var params = { 
    TableName : config.db,
    KeyConditions: {
      'id' : {
        AttributeValueList : [ { S : route.prefix } ],
        ComparisonOperator : 'EQ'
      }
    },
    Limit : config.galleryLimit
  };

  if (route.id) {
    params.KeyConditions['taken'] = {
      AttributeValueList : [ { N : route.id } ],
      ComparisonOperator : 'GT'
    };
  }

  return params;
};

exports.getImages = function(params, callback) {
    var db = new aws.DynamoDB();
    db.client.query(params, function(err, data) {
        if (err || !data || data.Count == 0) {
            console.log(err);
            callback(null, "Something bad happened. Carry on.");
        }
        else callback(data);
    });
};

exports.getImage = function(route, callback) {
    var params = { 
        TableName : config.db,
        KeyConditions: {
            'id' : {
                AttributeValueList : [ { S : route.prefix } ],
                ComparisonOperator : 'EQ'
            },
            'taken' : {
                AttributeValueList : [ { N : route.taken } ],
                ComparisonOperator : 'EQ'
            }
        },
        Limit : 1
    };

    var db = new aws.DynamoDB();
    db.client.query(params, function(err, data) {
        if (err || !data || data.Count == 0) {
            console.log(err);
            callback(null, "Something bad happened. Carry on.");
        }
        else callback(data);
    });
};