var zombie = require('zombie');
var World = function World(callback) {
    this.browser = new zombie();

    callback();
}
exports.World = World;
