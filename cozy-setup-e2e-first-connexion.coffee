# Test account registration and install of apps using the Wizard
#
# For more verbose output, add to command line --verbose --log-level=debug
#
casper.options.viewportSize = width: 1280, height: 800
casper.options.timeout = 60000
casper.options.waitTimeout = 20000

casper.cozy = {}

#
# Some casper event listener to ease debug
#

# Take a screenshot on exit
casper.on 'exit', ->
    casper.capture 'last.png'
    require('fs').write 'last.html', @getHTML()
# Display remote console messages
casper.on "remote.message", (msg) ->
    if typeof msg isnt 'string'
        msg = utils.serialize(msg, 2)
    casper.echo "Message: " + msg, "INFO"
# Display page errors
casper.on "page.error", (msg, trace) ->
    casper.echo "Error: " + msg, "ERROR"
    utils.dump trace.slice 0, 5
# Use a timeout to stop loading of pages using long polling
casper.on "load.started", ->
    casper.cozy.loadTimeout = setTimeout ->
        casper.log "Interrupting load", 'warning'
        casper.loadInProgress = false
    , 10000
casper.on "load.finished", ->
    clearTimeout casper.cozy.loadTimeout
casper.on "load.failed", ->
    clearTimeout casper.cozy.loadTimeout
# Inject polyfill for Function.prototype.bind, which isn't supported by PhantomJS < 2
casper.on 'page.initialized', ->
    @evaluate ->
        if not Function::bind
            Function::bind = (oThis) ->
                if typeof this isnt 'function'
                    throw new TypeError('Function.prototype.bind - what is trying to be bound is not callable')
                aArgs = Array::slice.call(arguments, 1)
                fToBind = this
                fNOP = ->
                fBound = ->
                    self = if this instanceof fNOP then this else oThis
                    fToBind.apply self, aArgs.concat(Array::slice.call(arguments))

                fNOP.prototype = @prototype
                fBound.prototype = new fNOP
                fBound
# Add more verbose debug logs
casper.on 'step.added', (step) ->
    stepName = step?.toString().replace(/function ([^\(]*)[.\s\S]*/gm, '$1')
    casper.log("Adding step " + stepName, 'debug')
casper.on 'step.created', (step) ->
    stepName = step?.toString().replace(/function ([^\(]*)[.\s\S]*/gm, '$1')
    casper.log("Creating step " + stepName, 'debug')
casper.on 'step.start', (step) ->
    stepName = step?.toString().replace(/function ([^\(]*)[.\s\S]*/gm, '$1')
    casper.log("Starting step " + stepName, 'debug')
casper.on 'step.complete', (step) ->
    stepName = step?.toString().replace(/function ([^\(]*)[.\s\S]*/gm, '$1')
    casper.log("Completed step " + stepName, 'debug')
casper.on 'step.timeout', ->
    casper.log("Timeout step ", 'debug')
casper.on 'step.error', (err) ->
    casper.log("Error step " + err, 'debug')


casper.test.begin 'Cozy need to be registered on first launch', (test) ->
    casper.start 'https://127.0.0.1/'

    casper.then ->
        casper.wait 500, ->
            test.assertTitle(
                'Cozy - Sign up', 'We need to be registered on first launch'
            )
            test.assertExists(
                'input[id="email-input"]', 'We found email input'
            )
            @sendKeys 'input#email-input', 'user@test.com'
            @sendKeys 'input#password-input', 'toto35ToTo!35'
            @sendKeys 'input#password-check-input', 'toto35ToTo!35'

    casper.then ->
        @click '#submit-btn'

        casper.waitUntilVisible '.alert-success', ->
            test.assertNotVisible(
                '.alert-error', 'No error message was displayed.'
            )
            test.assertVisible(
                '.alert-success', 'Success was successfully displayed.'
            )
            test.assertEval ->
                return __utils__.findOne('.alert-success').textContent.length > 0
            , 'We have success message have content'

    casper.then ->
        casper.waitForSelector 'dialog.wizard', ->
            test.assertTitle 'Cozy - Home', 'We are on homepage'
            test.assertVisible 'dialog.wizard > section:nth-child(1)', 'First panel of wizard is visible'
            test.assertNotVisible 'dialog.wizard > section:nth-child(2)', 'Second panel of wizard is visible'
            casper.click 'button.next'
            casper.waitUntilVisible 'dialog.wizard > section:nth-child(2)', ->
                test.assertVisible '#files-yes', 'Wizard - Files'
                casper.click '#files-yes'
                casper.waitUntilVisible 'dialog.wizard > section:nth-child(3)', ->
                    test.assertVisible '#emails-yes', 'Wizard - Emails'
                    casper.click '#emails-yes'
                    casper.waitUntilVisible 'dialog.wizard > section:nth-child(4)', ->
                        test.assertVisible '#contacts-yes', 'Wizard - Contacts'
                        casper.click '#contacts-yes'
                        casper.waitUntilVisible 'dialog.wizard > section:nth-child(5)', ->
                            test.assertVisible '#calendar-yes', 'Wizard - Calendar'
                            casper.click '#calendar-yes'
                            casper.waitUntilVisible 'dialog.wizard > section:nth-child(6)', ->
                                test.assertVisible '#photos-yes', 'Wizard - Photos'
                                casper.click '#photos-yes'
                                casper.waitUntilVisible 'dialog.wizard > section:nth-child(7)', ->
                                    test.assertVisible '#thanks-go-to-my-cozy', 'Wizard - End'
                                    casper.click '#thanks-go-to-my-cozy'
                                    casper.waitWhileVisible 'dialog.wizard', ->
                                        test.pass 'Wizard done'

    casper.then ->
        testApp = (name) ->
            casper.waitWhileVisible "#app-btn-#{name} img.icon", ->
                test.pass "#{name} is installed"

        ['files', 'emails', 'sync', 'contacts', 'calendar', 'photos'].forEach (name) ->
            testApp name


    casper.run ->
        test.done()


