# Standard library imports
from mako.template import Template
from textwrap import dedent

# Enthought library imports
from traits.api import HasTraits, Instance, Str, Float, Property, Tuple, Any

# Local imports
from jigna.api import PYNAME
from jigna.util.misc import get_value

class BasicEditor(HasTraits):

    # model object whose trait we are editing
    obj = Instance(HasTraits)

    # the name of the trait we are editing - this can be an extended trait name
    tname = Str

    # label to refer the trait
    label = Str

    # value of the trait
    value = Property(depends_on='[obj, tname]')

    ## Trait handlers #################################################

    def _get_value(self):
        return get_value(self.obj, self.tname)

    def _label_default(self):
        return self.tname

    ## Editor API #############################################################

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
                            <label for="${label}"> ${label}
                                <input type='number' ng-model='${tname}'
                                name='${label}' value='${value}'>
                            </label>
                        </div>
                        """)
        return Template(template_str).render(label=self.label,
                                             value=self.value,
                                             tname=self.tname)


class FloatEditor(BasicEditor):

    def html(self):
        template_str = dedent("""
                        <div class="editor float-editor">
                            <label for="${label}"> ${label}
                                <input type='number' ng-model='${tname}'
                                name='${label}' value='${value}'></label>
                        </div>
                        """)
        return Template(template_str).render(label=self.label,
                                             value=self.value,
                                             tname=self.tname)


class StringEditor(BasicEditor):

    def html(self):
        template_str = dedent("""
                        <div class="editor string-editor">
                            <label for="${label}"> ${label}
                                <input type='text' ng-model='${tname}'
                                name='${label}' value='${value}'>
                            </label>
                        </div>
                        """)
        return Template(template_str).render(label=self.label,
                                             value=self.value,
                                             tname=self.tname)

class BoolEditor(BasicEditor):

    def html(self):
        template_str = dedent("""
                        <div class="editor bool-editor">
                            <label for="${label}">
                                <input type='checkbox' ng-model='${tname}'
                                name='${label}' value='${label}' checked='${value}'>
                                ${label}
                            </label>
                        </div>
                        """)
        return Template(template_str).render(label=self.label,
                                             value=self.value,
                                             tname=self.tname)

class EnumEditor(BasicEditor):

    possible_values = Tuple

    def _possible_values_default(self):
        return self.obj.trait(self.tname).handler.values

    def html(self):
        template_str =  dedent("""
                        <label for="${label}"> ${label} </label>
                        <div>
                            % for i, val in enumerate(possible_values):
                                <input id="${label}_${i}" type='radio'
                                   ng-model='${tname}' value='${val}'>
                                    ${val}
                                </label>
                            % endfor
                            </div>
                        </div>
                        """)
        return Template(template_str).render(possible_values=self.possible_values,
                                            label=self.label,
                                            tname=self.tname)

class RangeEditor(BasicEditor):

    low = Float

    high = Float

    def _low_default(self):
        trait = self.obj.trait(self.tname)
        return trait.trait_type._low

    def _high_default(self):
        trait = self.obj.trait(self.tname)
        return trait.trait_type._high

    def html(self):
        template_str = dedent("""
                        <div class="editor float-editor">
                            <label for="${label}"> ${label}
                                <input type='range' ng-model='${tname}'
                                  name='${label}' value="${value}" min="${low}"
                                  max="${high}">
                            </label>
                        </div>
                        """)
        return Template(template_str).render(label=self.label,
                                             value=self.value,
                                             tname=self.tname,
                                             min=self.low,
                                             max=self.high)


class InstanceEditor(BasicEditor):

    instance_view = Any

    def _instance_view_default(self):
        from jigna.html_view import HTMLView
        import jigna.registry as registry
        model_name = "%s.%s"%(registry.registry['model_names'][id(self.obj)],
                                       self.tname)
        return HTMLView(model=self.value, model_name=model_name)

    def html(self):
        return Template("""
                        <label for="${label}">${label}</label>
                        <div style="border:solid 1px #ccc; padding: 5px"
                             class="editor bool-editor">
                            ${instance_html}
                        </div>
                        """).render(instance_html=self.instance_view.html,
                                    label=self.label)

    def js(self):
        return self.instance_view.js