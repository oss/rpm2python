Feature: Make sure the letters under
    The search bar lead to
    An alphabatized list

    Scenario: Click on "A"
        Given I am on the main page
        When I click on "A"
        Then the list should start with "A" and be alphabatized
