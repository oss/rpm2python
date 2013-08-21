var SearchWrapper = function() {
    this.World = require("../support/world.js").World;

    this.When(/^the user searches for '([^']*)'$/,
        function(search, callback) {
            this.browser.fill("#function_name", search).pressButton("#search_button",
                function() {
                    var results_table = this.browser.document.getElementById("resultsTable").getElementsByTagName("tr");
                    callback.pending();
                }
        }
}
