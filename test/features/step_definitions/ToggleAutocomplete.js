var ToggleAutocompleteWrapper = function() {
    this.World = require("../support/world.js").World;

    this.Given(/^I am on the (.*) page$/,
        function(page, callback) {
            if (page == 'main')
                page_url = 'index';
            this.browser.visit("http://127.0.0.1:5000/" + page_url, callback);
        }
    );

    this.When(/^I select "([^"]*)"$/,
        function(selection, callback) {
            this.browser.select("#searchby", selection, callback);
        }
    );

    this.Then(/^autocomplete should be (.*)$/,
        function(state, callback) {
            
        }
}
