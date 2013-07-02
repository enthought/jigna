# Standard library imports
from mako.template import Template
from textwrap import dedent

# Enthought library imports
from traits.api import HasTraits, Instance, Str

# Local imports
from jigna.session import PYNAME


class BasicEditor(HasTraits):

    obj = Instance(HasTraits)

    tname = Str

    def html(self):
        raise NotImplementedError

    def js(self):
        template_str = dedent("""
                       <%
                           from jigna.util.misc import serialize
                           value = serialize(getattr(obj, tname))
                       %>
                       $scope.${tname} = JSON.parse('${value}');
                       $scope.$watch('${tname}', function(newValue, oldValue) {
                           ${pyobj}.trait_set($scope.obj_id, '${tname}', newValue);
                       });
                       """)
        return Template(template_str).render(obj=self.obj, tname=self.tname,
                                             pyobj=PYNAME)


class IntEditor(BasicEditor):

    def html(self):
        template_str = dedent("""
                        <div class="editor int-editor">
                            <label for="${tname}"> ${tname}
                                <input type='number' ng-model='${tname}' name='${tname}'
                                value='${getattr(obj, tname)}'>
                            </label>
                        </div>
                        """)
        return Template(template_str).render(obj=self.obj, tname=self.tname)


class FloatEditor(BasicEditor):

    def html(self):
        template_str = dedent("""
                        <div class="editor float-editor">
                            <label for="${tname}"> ${tname}
                                <input type='number' ng-model='${tname}' name='${tname}'
                                value='${getattr(obj, tname)}'></label>
                        </div>
                        """)
        return Template(template_str).render(obj=self.obj, tname=self.tname)


class StringEditor(BasicEditor):

    def html(self):
        template_str = dedent("""
                        <div class="editor string-editor">
                            <label for="${tname}"> ${tname}
                                <input type='text' ng-model='${tname}' name='${tname}'
                                value='${getattr(obj, tname)}'>
                            </label>
                        </div>
                        """)
        return Template(template_str).render(obj=self.obj, tname=self.tname)


class BoolEditor(BasicEditor):

    def html(self):
        template_str = dedent("""
                        <div class="editor bool-editor">
                            <label for="${tname}">
                                <input type='checkbox' ng-model='${tname}' name='${tname}'
                                value='${tname}' checked='${getattr(obj, tname)}'>
                                ${tname}
                            </label>
                        </div>
                        """)
        return Template(template_str).render(obj=self.obj, tname=self.tname)


class EnumEditor(BasicEditor):

    def html(self):
        template_str = dedent("""
                        <div class="editor enum-editor">
                            <label for="${tname}"> ${tname} </label>
                            <div class="enum-elements">
                                % for value in obj.trait(tname).handler.values:
                                <label for="${tname}_${value}">
                                    <input id="${tname}_${value}" type='radio' ng-model='${tname}'
                                    value='${value}'>
                                    ${value}
                                </label>
                            % endfor
                            </div>
                        </div>
                        """)
        return Template(template_str).render(obj=self.obj, tname=self.tname)
        
class ListEditor(BasicEditor):
    
    def html(self):
        pass
            