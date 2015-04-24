var gulp = require('gulp');
var gutil= require('gulp-util');
var coffee = require('gulp-coffee');


js_files = './js/*.coffee'

gulp.task('coffee', function() {
  gulp.src(js_files)
    .pipe(coffee({bare: true}).on('error', gutil.log))
    .pipe(gulp.dest('./static/js/'))
});

gulp.task('watch', function() {
  gulp.watch(js_files, ['coffee']);
});
