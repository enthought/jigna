var app = angular.module('templating', ['jigna']);

app.run(function(){
    jigna.initialize();
})

app.directive('personView', function(){
    return {
        scope: {person: '='},
        templateUrl: 'template_person.html'
    }
})