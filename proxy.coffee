eyes = require('eyes')
haibu = require('haibu')

client = new haibu.drone.Client
  host: 'localhost'
  port: 9002


app =
   "user": "cozy"
   "name": "proxy"
   "domain": "localhost"
   "repository":
       "type": "git",
       "url": "https://frankrousseau@github.com/mycozycloud/cozy-proxy.git"
   "scripts":
       "start": "router.coffee"
   

client.clean app, (err, result) ->

    client.start app, (err, result) ->
      if err
        console.log 'Error spawning app: ' + app.name
        console.log err
        return eyes.inspect(err)

      console.log('Successfully spawned app:')
      eyes.inspect(result)


