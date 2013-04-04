# This program is suited only to manage your cozy installation from the inside
# Moreover app management works only for apps make by Cozy Cloud company.
# If you want a friendly application manager you should use the
# appmanager.coffee script.

require "colors"

program = require 'commander'
async = require "async"
request = require 'request'
exec = require('child_process').exec

haibu = require('haibu-api')
Client = require("request-json").JsonClient


statusClient = new Client("http://localhost:9002/")
homeUrl = "http://localhost:9103/"
proxyUrl = "http://localhost:9104/"
couchUrl = "http://localhost:5984/"
homeClient = new Client homeUrl

client = haibu.createClient
  host: 'localhost'
  port: 9002
client = client.drone


app_descriptor =
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
        app_descriptor.user = app
        console.log "Install started for #{app}..."

        client.clean app_descriptor, (err, result) ->
            client.start app_descriptor, (err, result) ->
                if err
                    console.log err
                    console.log "Install failed"
                else
                    console.log "#{app} sucessfully installed"

program
    .command("install_home <app>")
    .description("Install application via home app")
    .action (app) ->
        app_descriptor.name = app
        app_descriptor.git =
            "https://github.com/mycozycloud/cozy-#{app}.git"
        app_descriptor.user = app
        console.log "Install started for #{app}..."
        path = "api/applications/install"
        homeClient.post path, app_descriptor, (err, res, body) ->
            if err or res.statusCode isnt 200
                console.log err if err?
                console.log "Install failed"
                if body?
                    if body.msg? then console.log body.msg else console.log body
            else
                console.log "#{app} sucessfully installed"

program
    .command("uninstall_home <app>")
    .description("Install application via home app")
    .action (app) ->
        console.log "Uninstall started for #{app}..."
        path = "api/applications/#{app}/uninstall"
        homeClient.del path, (err, res, body) ->
            if err or res.statusCode isnt 200
                console.log err if err?
                console.log "Uninstall failed"
                if body?
                    if body.msg? then console.log body.msg else console.log body
            else
                console.log "#{app} sucessfully uninstalled"

program
    .command("uninstall <app>")
    .description("Remove application from haibu")
    .action (app) ->
        app_descriptor.name = app
        app_descriptor.user = app
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
        app_descriptor.user = app
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
        app.user = app
        client.stop app, (err) ->
            if err
                console.log "Stop failed"
                console.log err.result.error.message
            else
                console.log "#{app} sucessfully stopped"

program
    .command("brunch <app>")
    .description("Brunch application through haibu")
    .action (app) ->
        console.log "Brunch build #{app}..."
        app_descriptor.name = app
        app_descriptor.repository.url =
            "https ://github.com/mycozycloud/cozy-#{app}.git"
        app_descriptor.user = app
        statusClient.post "drones/#{app}/brunch", {brunch : app_descriptor}, \
             (err, res, body) ->
            if (res.statusCode isnt 200)
                console.log "Brunch failed"
                console.log body
            else
                console.log "#{app} sucessfully built"

program
    .command("restart <app>")
    .description("Restart application trough haibu")
    .action (app) ->
        console.log "Stopping #{app}..."

        client.stop app, (err) ->
            if err
                console.log "Stop failed"
                console.log err.result.error.message
            else
                console.log "#{app} sucessfully stopped"
                app_descriptor.name = app
                app_descriptor.repository.url =
                    "https://github.com/mycozycloud/cozy-#{app}.git"
                app_descriptor.user = app
                console.log "Starting #{app}..."

                client.start app_descriptor, (err, result) ->
                if err
                    console.log "Start failed"
                    console.log err
                else
                    console.log "#{app} sucessfully started"

program
    .command("update <app>")
    .description(
        "Update application (git + npm install) and restart it through haibu")
    .action (app) ->
        console.log "Update #{app}..."

        app_descriptor.name = app
        app_descriptor.repository.url =
            "https://github.com/mycozycloud/cozy-#{app}.git"
        app_descriptor.user = app

        path = "./node_modules/haibu/local/cozy/#{app}/cozy-#{app}/"
        exec "cd #{path}; git pull origin master; npm install --production", \
             (error, stdout, stderr) ->
            console.log stdout
            console.log error if error
            client.stop app, (err) ->
                client.start app_descriptor, (err) ->
                    if err
                        console.log "Update failed"
                        console.log err.result.error.message
                    else
                        console.log "#{app} sucessfully updated"

program
    .command("lightUpdate <app>")
    .description("Light update application through haibu")
    .action (app) ->
        console.log "Light update #{app}..."
        app_descriptor.name = app
        app_descriptor.repository.url =
            "https ://github.com/mycozycloud/cozy-#{app}.git"
        app_descriptor.user = app
        statusClient.post "drones/#{app}/light-update", \
             {update : app_descriptor}, (err, res, body) ->
            if (res.statusCode isnt 200)
                console.log "Update failed"
                console.log body
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
        console.log "Run script #{script} for #{app}..."
        path = "./node_modules/haibu/local/cozy/#{app}/cozy-#{app}/"
        child = exec "cd #{path}; coffee #{script}.coffee", \
                     (error, stdout, stderr) ->
            console.log stdout
            if error != null
                console.log "exec error: #{error}"
                console.log "stderr: #{stderr}"

program
    .command("script_arg <app> <script> <argument>")
    .description("Launch script that comes with given application")
    .action (app, script, argument) ->
        console.log "Run script #{script} for #{app}..."
        path = "./node_modules/haibu/local/cozy/#{app}/cozy-#{app}/"
        child = exec "cd #{path}; coffee #{script}.coffee #{argument}", \
                     (error, stdout, stderr) ->
            console.log stdout
            if error != null
                console.log "exec error: #{error}"
                console.log "stderr: #{stderr}"

program
    .command("reset-proxy")
    .description("Reset proxy routes list of applications given by home.")
    .action ->
        console.log "Reset proxy routes"

        statusClient.host = proxyUrl
        statusClient.get "routes/reset", (err) ->
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

        statusClient.host = proxyUrl
        statusClient.get "routes", (err, res, routes) ->

            if not err and routes?
                for route of routes
                    console.log "#{route} => #{routes[route]}"

program
    .command("status")
    .description("Give current state of cozy platform applications")
    .action ->
        checkApp = (app, host, path="") ->
            (callback) ->
                statusClient.host = host
                statusClient.get path, (err, res) ->
                    if err
                        console.log "#{app}: " + "down".red
                    else
                        console.log "#{app}: " + "up".green
                    callback()

        async.series [
            checkApp("haibu", "http://localhost:9002/", "version")
            checkApp("data-system", "http://localhost:9101/")
            checkApp("indexer", "http://localhost:9102/")
            checkApp("home", "http://localhost:9103/")
            checkApp("proxy", "http://localhost:9104/", "routes")
        ], ->
            statusClient.host = homeUrl
            statusClient.get "api/applications/", (err, res, apps) ->
                funcs = []
                if apps? and apps.rows?
                    for app in apps.rows
                        func = checkApp(app.name, "http://localhost:#{app.port}/")
                        funcs.push func
                    async.series funcs, ->

program
    .command("reinstall-all")
    .description("Reinstall all user applications")
    .action ->
        installApp = (app) ->
            (callback) ->
                console.log "Install started for #{app.name}..."
                app_descriptor.name = app.name
                app_descriptor.repository.url = app.git
                app_descriptor.user = app.user

                client.clean app_descriptor, (err, result) ->
                    client.start app_descriptor, (err, result) ->
                        if err
                            console.log err
                            console.log "Install failed"
                        else
                            console.log "#{app.name} sucessfully installed"
                        callback()

        statusClient.host = homeUrl
        statusClient.get "api/applications/", (err, res, apps) ->
            funcs = []
            if apps? and apps.rows?
                for app in apps.rows
                    func = installApp(app)
                    funcs.push func

                async.series funcs, ->
                    console.log "All apps reinstalled."
                    console.log "Reset proxy routes"

                    statusClient.host = proxyUrl
                    statusClient.get "routes/reset", (err) ->
                        if err
                            console.log err
                            console.log "Reset proxy failed."
                        else
                            console.log "Reset proxy succeeded."

program
    .command("backup <target>")
    .description("Start couchdb replication to the target")
    .action (target) ->
        client = new Client couchUrl
        data =
            source: "cozy"
            target: target
        client.post "_replicate", data, (err, res, body) ->
            if err
                console.log err
                console.log "Backup Not Started"
                process.exit 1
            else if not body.ok
                console.log body
                console.log "Backup start but failed"
                process.exit 1
            else
                console.log "Backup succeed"
                process.exit 0

program
    .command("*")
    .description("Display error message for an unknown command.")
    .action ->
        console.log 'Unknown command, run "coffee monitor --help"' + \
                    ' to know the list of available commands.'

program.parse(process.argv)
