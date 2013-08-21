var myHooks = function () {
    this.Before(function(callback) {
        this.browser.visit("http://127.0.0.1:5000/index", callback);
    });
};

module.exports = myHooks;
