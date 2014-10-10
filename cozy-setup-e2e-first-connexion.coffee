casper.options.viewportSize = width: 1280, height: 800

casper.test.begin 'Cozy need to be registered on first launch', (test) ->
    casper.start 'https://127.0.0.1/'

    casper.wait '500', ->
        test.assertTitle(
            'Cozy - Sign up', 'We need to be registered on first launch'
        )
        test.assertExists(
            'input[id="email-input"]', 'We found email input'
        )
        @echo 'We fill form'
        @sendKeys 'input#email-input', 'user@test.com'
        @sendKeys 'input#password-input', 'toto35ToTo!35'
        @sendKeys 'input#password-check-input', 'toto35ToTo!35'

    casper.then ->
        @echo 'We click on "Send" button'
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

    casper.waitForUrl /https:\/\/127.0.0.1\/$/, ->
        test.assertTitle 'Cozy - Home', 'We are on homepage'

    casper.run ->
        test.done()
