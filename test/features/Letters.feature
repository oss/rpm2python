Feature: Make sure the letters under
    The search bar lead to
    An alphabatized list

    Scenario: Click on "A"
        When I click on "A"
        Then the list should start with "A" and be alphabatized
