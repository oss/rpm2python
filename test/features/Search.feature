Feature: Search the database for
    Packages that match what the
    User typed in

    Scenario: The user searches for 'babel'
        When the user searches for 'babel'
        Then the number of results should match the database
