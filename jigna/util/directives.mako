<%!
    from jigna.api import APPNAME as appname
%>

window.app = angular.module('${appname}', []);

// directive to convert to numbers
window.app.directive('toNumber', function () {
    return {
        require: 'ngModel',
        link: function (scope, elem, attrs, ctrl) {
            ctrl.$parsers.push(function (value) {
                return parseFloat(value || '');
            });
        }
    };
});