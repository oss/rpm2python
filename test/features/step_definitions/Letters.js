var LettersWrapper = function() {
    this.World = require("../support/world.js").World;

    this.When(/^I click on "([^"]*)"$/,
        function(letter, callback) {
            this.browser.visit("http://127.0.0.1:5000/" + letter, callback);
        }
    );

    this.Then(/^the list should start with "([^"]*)" and be alphabatized$/,
        function(letter, callback) {
            var results_table = this.browser.document.getElementById("resultsTable").getElementsByTagName("tr");
            var prev = "";
            for (var i = 1; i < results_table.length; i++) {
                var curr;
                if (prev > (curr = results_table[i].getElementsByTagName("td")[0].textContent.toLowerCase()))
                    callback.fail(new Error('Page "' + letter + '" not in alphabetical order'));
                if (curr.charAt(0).toUpperCase() != letter)
                    callback.fail(new Error(curr + 'doesn\'t start with "A"'));
                prev = curr;
            }
            callback();
        }
    );
};

module.exports = LettersWrapper;
