# Standard library imports
from mako.template import Template
from textwrap import dedent

# Enthought library imports
from traits.api import HasTraits, Instance, Str, Float
from traitsui.api import EditorFactory

# Local imports
from jigna.api import PYNAME

class BasicEditor(EditorFactory):

    obj = Instance(HasTraits)

    tname = Str

    def html(self):
        raise NotImplementedError

    def js(self):
        return ""

    def setup_session(self, session=None):
        """ Any setup steps that need to be performed before the session starts
        """
        pass


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

class RangeEditor(BasicEditor):

    min = Float(0.0)

    max = Float(100.0)

    def html(self):
        template_str = dedent("""
                        <div class="editor float-editor">
                            <label for="${tname}"> ${tname}
                                <input type='range' ng-model='${tname}' name='${tname}'
                                value="${getattr(obj, tname)}" min="${min}"
                                max="${max}">
                            </label>
                        </div>
                        """)
        return Template(template_str).render(obj=self.obj, tname=self.tname,
                                             min=self.min, max=self.max)

class ListEditor(BasicEditor):

    def html(self):
        raise NotImplementedError


class InstanceEditor(BasicEditor):

    def __init__(self, **traits):
        super(InstanceEditor, self).__init__(**traits)
        self._instance = getattr(self.obj, self.tname)
        from jigna.html_view import HTMLView
        self._instance_view = HTMLView(model=self._instance)

    def html(self):
        return Template("""
                        <label for="${tname}">${tname}</label>
                        <div style="border:solid 1px #ccc; padding: 5px"
                             class="editor bool-editor">
                            ${instance_html}
                        </div>
                        """).render(instance_html=self._instance_view.html,
                                    tname=self.tname)

    def js(self):
        return self._instance_view.js
