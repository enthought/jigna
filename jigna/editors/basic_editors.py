# Standard library imports
from mako.template import Template
from textwrap import dedent

# Enthought library imports
from traits.api import HasTraits, Instance, Str

# Local imports
from jigna.api import PYNAME
from jigna.html_view import HTMLView

class BasicEditor(HasTraits):

    obj = Instance(HasTraits)

    tname = Str

    obj_view = Instance(HTMLView)

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
                           ${pyobj}.set_trait($scope.obj_id, '${tname}', newValue);
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
        template_str =  dedent("""
                        <label for="${tname}"> ${tname} </label>
                        <div>
                            % for value in obj.trait(tname).handler.values:
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
        raise NotImplementedError


class InstanceEditor(BasicEditor):

    obj_view = Instance(HTMLView)

    def html(self):
        instance = getattr(self.obj, self.tname)
        view = HTMLView(model=instance)
        view.generate_html()
        return Template("""
                        <label for="${tname}">${tname}</label>
                        <div style="border:solid 1px #ccc; padding: 5px"
                             class="editor bool-editor">
                            ${instance_html}
                        </div>
                        """).render(instance_html=view.html, tname=self.tname)

    def js(self):
        instance = getattr(self.obj, self.tname)
        view = HTMLView(model=instance, session=self.obj_view.session)
        view.setup_session()
        return view.js
