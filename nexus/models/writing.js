
var mongoose = require(mongoose)

var Schema = mongoose.schema;

var writingSchema = new Schema(
    {
        display : {type : Boolean, required : true},
        style : {type : Schema.Types.ObjectId, ref : "writingStyle", required : true},
        name : {type : String, required : true, maxLength : 100},
        summary : {type : String, required : true},
        content : {type : String, required : false},
        url : {type : String, required : true}, 
        img: {data: Buffer, contentType: String, required : false}
    }
);

/** Create a function to return an array with all the different styles
 * 
 * 
writingSchema 
.virtual('styles')
.get(function(){
    function(req, res) { unique_id(writing.style)}
    return res
});
*/

module.exports = mongoose.model('writing', writingSchema);