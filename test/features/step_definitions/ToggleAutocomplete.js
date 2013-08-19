var ToggleAutocompleteWrapper = function() {
    this.World = require("../support/world.js").World;

    this.Given(/^I am on the (.*) page$/,
        function(page, callback) {
            if (page == 'main')
                page_url = 'index';
            this.browser.visit("http://127.0.0.1:5000/" + page_url, callback);
        }
    );

    this.When(/^I select '([^']*)'$/,
        function(selection, callback) {
            callback.pending();
            this.browser.select("Search by", selection, callback);
        }
    );

    this.Then(/^autocomplete should be (.*)$/,
        function(state, callback) {
            callback.pending();
            if (this.browser.document.querySelector("ul#ui-id-1").style.display != 'none') {
                if (state == 'enabled')
                    callback();
                else
                    callback.fail(new Error("debug"));
            } else if (state == 'disabled')
                callback();
            else {
                console.log(this.browser.document.querySelector("ul#ui-id-1").style.display);
                callback.fail(new Error("Autocomplete is not " + state + " when it should be"));
            }
        }
    );
}
module.exports = ToggleAutocompleteWrapper;
