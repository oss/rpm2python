var zombie = require('zombie');
var sql = require('sqlite3').verbose();
var World = function World(callback) {
    this.browser = new zombie();
    this.cent5 = new sql.Database('cent5.db');
    this.cent6 = new sql.Database('cent6.db');
    callback();
}
exports.World = World;
