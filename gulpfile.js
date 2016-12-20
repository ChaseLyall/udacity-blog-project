var gulp = require('gulp'),
    prettify = require('gulp-html-prettify');

gulp.task('templates', function() {
  gulp.src('./templates/*.html')
    .pipe(prettify({indent_char: ' ', indent_size: 4}))
    .pipe(gulp.dest('./templates/'))
});

gulp.task('default', function() {
  // place code for your default task here
});