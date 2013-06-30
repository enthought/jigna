<%!
    from jigna.util.misc import serialize
%>

<%def name="js_for_trait(obj, tname)">
    <%
        value = serialize(getattr(obj, tname))
    %>
    $scope.${tname} = JSON.parse('${value}');
    $scope.$watch('${tname}', function(newValue, oldValue) {
        ${pyobj}.trait_set('${tname}', newValue);
    });
</%def>

function ${obj_class}_Ctrl($scope) {
    % for tname in obj.editable_traits():
        ${js_for_trait(obj, tname)}    
    % endfor
    
    <%block name="util_funcs">
    $scope.scoped = function() {
        var func, largs;
        func = arguments[0], largs = 2 <= arguments.length ? __slice.call(arguments, 1) : [];
        if ($scope.$$phase) {
        return func.apply(this, largs);
        } else {
        return $scope.$apply(function() {
            return func.apply(this, largs);
        });
        }
    };
    </%block>
}