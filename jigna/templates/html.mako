<%!
    from traits.api import Int, Str, Bool, Enum, Float
%>

<%def name="html_for_trait(obj, tname)">
    <%
        trait_type = obj.trait(tname).trait_type
    %>
    % if isinstance(trait_type, Int):
        <label for="${tname}"> ${tname} </label>
        <input type='number' ng-model='${tname}' name='${tname}'
               value='${getattr(obj, tname)}'>
    % endif
    
    % if isinstance(trait_type, Float):
        <label for="${tname}"> ${tname} </label>
        <input type='number' ng-model='${tname}' name='${tname}'
               value='${getattr(obj, tname)}'>
    % endif
    
    % if isinstance(trait_type, Str):
        <label for="${tname}"> ${tname} </label>
        <input type='text' ng-model='${tname}' name='${tname}'
               value='${getattr(obj, tname)}'>
    % endif
    
    % if isinstance(trait_type, Bool):
        <label for="${tname}"> ${tname} </label>
        <input type='checkbox' ng-model='${tname}' name='${tname}'
               value='${tname}' checked='${getattr(obj, tname)}'>
    % endif
    
    % if isinstance(trait_type, Enum):
        <label for="${tname}"> ${tname} </label>
        <div>
            % for value in obj.trait(tname).handler.values:
                <input id="${tname}_${value}" type='radio' ng-model='${tname}' 
                       value='${value}'>
                <label for="${tname}_${value}"> ${value}</label>
            % endfor
        </div>
    % endif
</%def>

<%block name="html">
<!DOCTYPE html>
<html ng-app>
    <head>
        <script type="text/javascript" src="${jquery}"></script>
        <script type="text/javascript" src="${angularjs}"></script>
        <script type="text/javascript">
            ${jignajs}
        </script>
        <style>
            ${jignacss}
        </style>
    </head>
    
    <body>
        <div ng-controller="${obj_class}_Ctrl" 
             id="id_${obj_id}" 
             class="class_${obj_class}">
             % for tname in obj.editable_traits():
               <div>
                  ${html_for_trait(obj, tname)}
               </div>
             % endfor
        </div>
    </body>
</html>
</%block>
