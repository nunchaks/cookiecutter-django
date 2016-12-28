
////////////////////////////////
		//Setup//
////////////////////////////////

// Plugins
var gulp = require('gulp'),
      pjson = require('./package.json'),
      gutil = require('gulp-util'),
      sass = require('gulp-sass'),
      autoprefixer = require('gulp-autoprefixer'),
      cssnano = require('gulp-cssnano'),
      rename = require('gulp-rename'),
      del = require('del'),
      plumber = require('gulp-plumber'),
      pixrem = require('gulp-pixrem'),
      uglify = require('gulp-uglify'),
      imagemin = require('gulp-imagemin'),
      exec = require('child_process').exec,
      runSequence = require('run-sequence'),
      connect = require('gulp-connect');
      //browserSync = require('browser-sync').create(),
      //reload = browserSync.reload;


// Relative paths function
var pathsConfig = function (appName) {
  this.app = "./" + (appName || pjson.name);

  return {
    app: this.app,
    templates: this.app + '/templates',
    css: this.app + '/static/css',
    sass: this.app + '/static/sass',
    fonts: this.app + '/static/fonts',
    images: this.app + '/static/images',
    js: this.app + '/static/js',
  }
};

var paths = pathsConfig();

////////////////////////////////
		//Tasks//
////////////////////////////////

// Styles autoprefixing and minification
gulp.task('styles', function() {
  return gulp.src(paths.sass + '/project.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(plumber()) // Checks for errors
    .pipe(autoprefixer({browsers: ['last 2 version']})) // Adds vendor prefixes
    .pipe(pixrem())  // add fallbacks for rem units
    .pipe(gulp.dest(paths.css))
    .pipe(rename({ suffix: '.min' }))
    .pipe(cssnano()) // Minifies the result
    .pipe(gulp.dest(paths.css))
    .pipe(connect.reload())
});

// Javascript minification
gulp.task('scripts', function() {
  return gulp.src(paths.js + '/project.js')
    .pipe(plumber()) // Checks for errors
    .pipe(uglify()) // Minifies the js
    .pipe(rename({ suffix: '.min' }))
    .pipe(gulp.dest(paths.js))
    .pipe(connect.reload())
});

// Image compression
gulp.task('imgCompression', function(){
  return gulp.src(paths.images + '/*')
    .pipe(imagemin()) // Compresses PNG, JPEG, GIF and SVG images
    .pipe(gulp.dest(paths.images))
    .pipe(connect.reload())
});

// Update if html change
gulp.task('html', function () {
  gulp.src(paths.templates + '/**/*.html')
    .pipe(connect.reload())
});

// Run django server
gulp.task('runServer', function() {
  exec('python manage.py runserver', function (err, stdout, stderr) {
    console.log(stdout);
    console.log(stderr);
  });
});

// Browser sync server for live reload
/*gulp.task('browserSync', function() {
    browserSync.init(
      [paths.css + "/*.css", paths.js + "*.js", paths.templates + '*.html'], {
        proxy:  "localhost:8000"
    });
});*/
gulp.task('connect', function() {
  connect.server({
    livereload: true
  });
});


// Default task
gulp.task('default', function() {
    runSequence(['styles', 'scripts', 'imgCompression'], 'runServer', 'connect', 'watch');
});

////////////////////////////////
		//Watch//
////////////////////////////////

// Watch
gulp.task('watch', function() {

  gulp.watch(paths.sass + '/*.scss', ['styles']);
  gulp.watch(paths.js + '/*.js', ['scripts']);
  //gulp.watch(paths.js + '/*.js', ['scripts']).on("change", reload);
  gulp.watch(paths.images + '/*', ['imgCompression']);
  gulp.watch(paths.templates + '/**/*.html', ['html']);
  //gulp.watch(paths.templates + '/**/*.html').on("change", reload);

});
