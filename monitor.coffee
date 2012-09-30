require "colors"
program = require 'commander'
async = require "async"

haibu = require('haibu')
Client = require("request-json").JsonClient

statusClient = new Client("")
homeUrl = "http://localhost:3000/"
homeClient = new Client homeUrl

client = new haibu.drone.Client
  host: 'localhost'
  port: 9002


app_descriptor =
   "user": "cozy"
   "domain": "localhost"
   "repository":
       "type": "git",
   "scripts":
       "start": "server.coffee"

program
  .version('0.0.1')
  .usage('<action> <app>')

program
    .command("install <app>")
    .description("Install application in haibu")
    .action (app) ->
        app_descriptor.name = app
        app_descriptor.repository.url =
            "https://github.com/mycozycloud/cozy-#{app}.git"
        console.log "Install started for #{app}..."
        
        client.clean app_descriptor, (err, result) ->
            client.start app_descriptor, (err, result) ->
                if err
                    console.log err
                    console.log "Install failed"
                else
                    console.log "#{app} sucessfully installed"
 
program
    .command("uninstall <app>")
    .description("Remove application from haibu")
    .action (app) ->
        app_descriptor.name = app
        console.log "Uninstall started for #{app}..."
        
        client.clean app_descriptor, (err, result) ->
            if err
                console.log "Uninstall failed"
                console.log err
            else
                console.log "#{app} sucessfully uninstalled"

program
    .command("start <app>")
    .description("Start application through haibu")
    .action (app) ->
        app_descriptor.name = app
        app_descriptor.repository.url =
            "https://github.com/mycozycloud/cozy-#{app}.git"
        console.log "Starting #{app}..."
        
        client.start app_descriptor, (err, result) ->
            if err
                console.log "Start failed"
                console.log err
            else
                console.log "#{app} sucessfully started"

program
    .command("stop <app>")
    .description("Stop application through haibu")
    .action (app) ->
        console.log "Stopping #{app}..."
        
        client.stop app, (err) ->
            if err
                console.log "Stop failed"
                console.log err.result.error.message
            else
                console.log "#{app} sucessfully stopped"

program
    .command("update <app>")
    .description("Update application through haibu")
    .action (app) ->
        console.log "Update #{app}..."
        
        client.stop app, (err) ->
            client.start app, (err) ->
                if err
                    console.log "Update failed"
                    console.log err.result.error.message
                else
                console.log "#{app} sucessfully updated"

program
    .command("uninstall-all")
    .description("Uninstall all apps from haibu")
    .action (app) ->
        console.log "Uninstall all apps..."
        
        client.cleanAll (err) ->
            if err
                console.log "Uninstall all failed"
                console.log err.result.error.message
            else
                console.log "All apps sucessfully uinstalled"

program
    .command("script <app> <script>")
    .description("Launch script that comes with given application")
    .action (app, script) ->
        exec = require('child_process').exec
        console.log "Run script #{script} for #{app}..."
        path = "./node_modules/haibu/local/cozy/#{app}/cozy-#{app}/"
        child = exec "cd #{path}; coffee #{path}#{script}.coffee", \
                     (error, stdout, stderr) ->
            console.log "stdout: #{stdout}"
            console.log "stderr: #{stderr}"
            if error != null
                  console.log "exec error: #{error}"
program
    .command("status")
    .description("Give current state of cozy platform main applications")
    .action ->
        checkApp = (app, host, path="") ->
            (callback) ->
                statusClient.host = host
                statusClient.get "", (err, res) ->
                    if err
                        console.log "#{app}: " + "down".red
                    else
                        console.log "#{app}: " + "up".green
                    callback()

        async.series [
            checkApp("haibu", "http://localhost:9002/", "version")
            checkApp("data-system", "http://localhost:7000/")
            checkApp("home", "http://localhost:3000/")
            checkApp("proxy", "http://localhost:4000/", "routes")
            checkApp("indexer", "http://localhost:5000/")
        ], ->
            statusClient.host = "http://localhost:3000/"
            statusClient.get "api/applications/", (err, res, apps) ->
                funcs = []
                for app in apps.rows
                    func = checkApp(app.name, "http://localhost:#{app.port}/")
                    funcs.push func
                async.series funcs, ->
                
program.parse(process.argv)
