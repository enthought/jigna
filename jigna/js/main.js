require(['angular', 'jigna-angular'], function(angular, jigna_app){
    // Bootstrap the jigna-angular application when the document is ready
    $(document).ready(function(){
        angular.bootstrap(document, [jigna_app.name]);
    });
});
