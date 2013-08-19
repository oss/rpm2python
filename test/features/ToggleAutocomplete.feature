Feature: Autocomplete turns off
    When the user does not have
    Name selected

    Scenario: Name is selected
        Given I am on the main page
        When I select 'Name'
        Then autocomplete should be enabled
    
    Scenario: Description is selected
        Given I am on the main page
        When I select 'Description'
        Then autocomplete should be disabled
