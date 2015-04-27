var gulp = require('gulp');
var gutil= require('gulp-util');
var coffee = require('gulp-coffee');
var less = require('gulp-less');


js_files = './js/*.coffee'
css_files = './styles/*.less'

gulp.task('coffee', function() {
  gulp.src(js_files)
    .pipe(coffee({bare: true}).on('error', gutil.log))
    .pipe(gulp.dest('./static/js/'))
});

gulp.task('less', function() {
  return gulp.src(css_files)
    .pipe(less().on('error', gutil.log))
    .pipe(gulp.dest('./static/css/'))
});

gulp.task('watch', function() {
  gulp.watch(js_files, ['coffee']);
  gulp.watch(css_files, ['less']);
});
