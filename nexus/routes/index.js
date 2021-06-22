var express = require('express');
var router = express.Router();

/** 
 * Import all the models
 * Decide what objects we are passing for sections (look at old django code)
 * How are the urls being managed
 * Where are all the models being passed and defined
 * Does everything need to be dynamic ?
*/ 
//Import the mongoose module
var mongoose = require('mongoose');

//Set up default mongoose connection
var mongoDB = "mongodb+srv://cluster0.zwnic.mongodb.net/Berd"
mongoose.connect(mongoDB, {useNewUrlParser: true, useUnifiedTopology: true});

//Get the default connection
var db = mongoose.connection;

//Bind connection to error event (to get notification of connection errors)
db.on('error', console.error.bind(console, 'MongoDB connection error:'));


router.get('/', function(req, res, next) {
  res.render('index', { title: 'Parvfection' });
});

router.get('/parv', function(req, res, next) {
  res.render('parv', {})
})


router.get('/writings', function(req, res, next){
  res.render('writings', {writingsModel : "writingTypeInstance"})
});

//** Dropdown of pieces instead of a new page */

router.get('/writings/*', function(req, res, next){
  res.render('$section.url', {writingsModel : 'writingsInstance.matchedInstances'})
});


router.get('/books', function(req, res, next){
  res.render('books', {bookModel : 'booksInstance'})
});

router.get('/books/*', function(req, res, next){
  res.render('$bookName.url', {bookModel : 'bookInstance.matchedInstances'})
});

router.get('/photos', function(req, res, next) {
  res.render('photos', {photoAlbumsModel : 'albumInstance'})
});

router.get('/photos/*<some_string:url>', function(req, res, next){
  res.render('matchAlbum.url', {photosModel : 'photosInstance.matchedInstances'})
});

router.get('/impList', function(req, res, next){
  res.render('impList', {impListModel : 'listInstance'})
});

router.get('/projects', function(req, res, next){
  res.render('projects', {projectModel : 'projectInstance'})
});

router.get('/about', function(req, res, next){
  res.render('about', {})
});

module.exports = router;
