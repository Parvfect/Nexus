
var mongoose = require('mongoose')

var Schema = mongoose.schema;

var writingStyleSchema = new Schema(
    {   
        name : {type : String, required : true, maxLength : 100},
        description : {type : String, required : true, maxLength : 100}
    }
);

writingStyleSchema 
.virtual()
.get(function(){
    return this.name
});


module.exports = mongoose.model('writingStyle', writingStyleSchema);

