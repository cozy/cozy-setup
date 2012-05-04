/* Copyright (c) 2009-2010 Marak Squires, Elijah Insua, Fedor Indutny - http://github.com/marak/node_mailer
 
Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:
 
The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
*/

var SMTPClient = require("nodemailer").SMTPClient;
var EmailMessage = require("nodemailer").EmailMessage;
var fs = require('fs');
var mustache = require('../vendor/mustache');
var _templateCache = {};

function SMTPClientPool() {
  this.servers = {};
}
SMTPClientPool.prototype.addClient = function(port,host,options) {
  if(this.servers[host] && this.servers[host][options.user]) return;
  var hostClients = this.servers[host] || (this.servers[host] = {});
  var pool = this;
  var client = hostClients[options.user] = new SMTPClient(host,port,options);
  client.on("close",function() {
    if(client == hostClients[options.user]) {
      //only because this could be crazy long lived and dynamic
      delete hostClients[options.user];
      if(Object.keys(hostClients).length == 0) {
	delete pool.servers[host]
      }
    }
  })
  client.on("empty",function(){
	delete hostClients[options.user];
	client.close();})
}

SMTPClientPool.prototype.send = function send(message, callback) {
  var hostpool = this.servers[message.SERVER.host]
  if(!hostpool) hostpool = {};
  var client = hostpool[message.SERVER.user]
  if(!client) {
    client = hostpool[message.SERVER.user] = new SMTPClient(message.SERVER.host,message.SERVER.port,message.SERVER);
    client.on("close",function() {
      if(client == hostpool[message.SERVER.user]) {
          //only because this could be crazy long lived and dynamic
          delete hostpool[message.SERVER.user];
          if(Object.keys(hostpool).length == 0) {
            delete pool.servers[host]
          }
        }
    })
    client.on("empty",function(){
     delete hostpool[message.SERVER.user];
     client.close();})
  }
  client.sendMail(message,callback);
  client.on('error', callback);
}


function merge(x,y) {
  var z = {};
  for(var k in x) {
    z[k] = x[k];
  }
  for(var k in y) {
    z[k] = y[k];
  }
  return z;
}

var pool = new SMTPClientPool();

exports.send = function node_mail(message, callback) {
  var server = {
    host: message.host,
    hostname: message.domain,
    port: + message.port,
    use_authentication: message.authentication,
    ssl: message.ssl,
    user: message.username && message.username.toString(),
    pass: message.password && message.password.toString(),
    debug: message.debug || false
  };
  if(message.username || message.password) {
    pool.addClient(server.port, server.host, server);
  }

  function dispatchMail(message, server, callback) {
      var _message = {
          to: message.to,
          sender: message.from,
          subject: message.subject,
          server: server,
          debug: message.debug
      };
      if(message.html)_message.html = message.html;
      pool.send(new EmailMessage(merge(message, _message)), callback);
  }

  // If a template was passed in as part of the message
  if (message.template) {
    // If the template path is in the cache
    if (_templateCache[message.template]) {
      // If the template is already fully loaded in the cahe
      if (_templateCache[message.template].loaded) {
        // Use the cached template and send the email
        message.html = mustache.to_html(_templateCache[message.template].template, message.data);
        dispatchMail(message, server, callback);
      }
      else {
        // We've started to load the template, but it's not loaded yet. queue up this message to be sent later
        _templateCache[message.template].queue.push(message);
      }
    }
    else {
      // The template path wasn't found in the cache, start to load the template
      _templateCache[message.template]          = {};
      _templateCache[message.template].loaded   = false;
      _templateCache[message.template].template = '';
      _templateCache[message.template].queue    = [];

      fs.readFile(message.template, function(err, result){
        if (err) {
          callback(err);
          return;
        }

        _templateCache[message.template].template = result.toString();
        _templateCache[message.template].loaded   = true;

        // "Drain" the queue
        _templateCache[message.template].queue.push(message);
        _templateCache[message.template].queue.forEach(function(msg, i){
          msg.html = mustache.to_html(_templateCache[message.template].template, msg.data);
          dispatchMail(msg, server, callback);
        });

        // Clear the queue out
        _templateCache[message.template].queue = [];
      });
    }
  }
  else { // No template being used
    dispatchMail(message, server, callback);
  }
};
