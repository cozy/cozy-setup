require "colors"

program = require 'commander'
async = require "async"
exec = require('child_process').exec

haibu = require('haibu-api')
Client = require("request-json").JsonClient


url = "http://localhost:9104/"
client = new Client url

app_descriptor =
   "user": "cozy"
   "domain": "localhost"
   "repository":
       "type": "git",
   "scripts":
       "start": "server.coffee"

configureClient = (callback) ->
    client.host = program.url if program.url?
    client.post "login", password: program.password, (err, res) ->
        if err or res.statusCode != 200
            console.log "Cannot get authenticated"
        else
            callback()

program
.version('0.1.0')
  .usage('<action> <app>')
  .option('-u, --url <url>',
          'set url where lives your Cozy Cloud, default to localhost')
  .option('-p, --password <password>',
          'Password required to connect on your Cozy Cloud')


program
    .command("install <app> <repo> [branch]")
    .description("Install given application from its repository")
    .action (app, repo, branch) ->
        configureClient ->
            app_descriptor.name = app
            app_descriptor.git = repo
            app_descriptor.branch = branch

            console.log "Install started for #{app}..."
            path = "api/applications/install"
            client.post path, app_descriptor, (err, res, body) ->
                if err or res.statusCode isnt 201
                    console.log err if err?
                    console.log "Install failed"
                    if body?
                        if body.msg?
                            console.log body.msg
                        else
                            console.log body
                else
                    console.log "#{app} sucessfully installed"

  
program
    .command("uninstall <app>")
    .description("Uninstall given application")
    .action (app) ->
        console.log "Uninstall started for #{app}..."
        configureClient ->
            path = "api/applications/#{app}/uninstall"
            client.del path, (err, res, body) ->
                if err or res.statusCode isnt 200
                    console.log err if err?
                    console.log "Uninstall failed"
                    if body?
                        if body.msg?
                            console.log body.msg
                        else
                            console.log body
                else
                    console.log "#{app} sucessfully uninstalled"

program
    .command("update <app>")
    .description(
        "Update application (git + npm install) and restart it through haibu")
    .action (app) ->
        console.log "Update #{app}..."
        configureClient ->
            path = "api/applications/#{app}/update"
            client.put path, {}, (err, res, body) ->
                if err or res.statusCode isnt 200
                    console.log err if err?
                    console.log "Update failed"
                    if body?
                        if body.msg?
                            console.log body.msg
                        else
                            console.log body
                else
                    console.log "#{app} sucessfully updated"

program
    .command("reset-proxy")
    .description("Reset proxy routes list of applications given by home.")
    .action ->
        console.log "Reset proxy routes"
        client.host = program.url if program.url?
        client.get "routes/reset", (err) ->
            if err
                console.log err
                console.log "Reset proxy failed."
            else
                console.log "Reset proxy succeeded."

program
    .command("routes")
    .description("Display routes currently configured inside proxy.")
    .action ->
        console.log "Display proxy routes..."
        client.host = program.url if program.url?
        
        client.get "routes", (err, res, routes) ->
            if not err and routes?
                console.log "#{route} => #{routes[route]}" for route of routes
                
program
    .command("status")
    .description("Give current state of cozy platform applications")
    .action ->

        checkApp = (app) ->
            (callback) ->
                if app isnt "home" and app isnt "proxy"
                    path = "apps/#{app}/"
                else path = ""

                client.get path, (err, res) ->
                    if err or res.statusCode != 200
                        console.log "#{app}: " + "down".red
                    else
                        console.log "#{app}: " + "up".green
                    callback()

        checkStatus = ->
            async.series [
                checkApp("home")
                checkApp("proxy", "routes")
            ], ->
                client.get "api/applications/", (err, res, apps) ->
                    if err
                        console.log err
                    else
                        funcs = []
                        if apps? and typeof apps == "object"
                            funcs.push checkApp(app.name) for app in apps.rows
                            async.series funcs, ->
     
        configureClient checkStatus

program
    .command("*")
    .description("Display error message for an unknown command.")
    .action ->
        console.log 'Unknown command, run "coffee monitor --help"' + \
                    ' to know the list of available commands.'
                    
program.parse(process.argv)
