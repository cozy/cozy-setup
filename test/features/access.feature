Feature: Test Cozy installation 

    Scenario: Access to home page
        Given I visit the url "https://33.33.33.10:80/"
        When I look around
        Then I should see "Cozy" somewhere in the page

    Scenario: Access to note page (forbidden)
        Given I visit the url "https://33.33.33.10:80/apps/notes/"
        When I look around
        Then I should see "Forbidden" somewhere in the page

    Scenario: Register and log in
        Given I visit the url "https://33.33.33.10:80/"
        When I fill in the field with the id "register-email" with "test@mycozycloud.com"
        And I fill in the field with the id "register-password" with "testtest"
        And I hit enter
        And I wait for a second 
        And I look around
        Then I should see "Account" somewhere in the page
        Then I should see "Notes" somewhere in the page

    Scenario: Access to note page (authentified)
        Given I visit the url "https://33.33.33.10:80/apps/notes/"
        When I look around
        Then I should see "create" somewhere in the page


    #Scenario: Access to Notes 
    #    When I go on note application
    #    When I logout
    
    #Scenario: Logout and forbidden access 
