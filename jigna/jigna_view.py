#
# Enthought product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#


# Standard library.
import json
from mako.template import Template
from traits.api import Dict, HasTraits, Instance, Str, TraitInstance

# Jigna libary.
from jigna.core.html_widget import HTMLWidget
from jigna.core.wsgi import JinjaRenderer


#### HTML templates ###########################################################

DOCUMENT_HTML_TEMPLATE = """
<html ng-app>
  <head>
    <script type="text/javascript" src="${jquery}"></script>
    <script type="text/javascript" src="${angular}"></script>
    <script type="text/javascript" src="${jigna}"></script>
  </head>

  <body>
    ${body_html}
  </body>
</html>
"""

MODEL_NAME = "model"


class JignaView(HasTraits):
    """ A factory for HTML/AngularJS based user interfaces. """

    #### 'JignaView' protocol #################################################

    #: The HTML for the *body* of the view's document.
    html = Str

    def show(self, model, traits=None):
        """ Create and show a view of the given model. """
        if traits is None:
            traits = model.editable_traits()

        self._id_to_object_map[str(id(model))] = model

        self._bind_python_to_js(model, traits)

        self._widget = self._create_widget()

        html = self._generate_html(model, traits)
        self._widget.load_html(html)

        def add_model():
            print "adding model"
            self._widget.execute_js("console.log($(document.body).scope())")
            self._add_model(model, MODEL_NAME)
        self._widget.on_trait_change(add_model, 'loaded')

        self._widget.control.show()

        return

    #### Private protocol #####################################################
    
    #: The ID to model mapping.
    _id_to_object_map = Dict

    def _bind_python_to_js(self, model, traits):
        """ Bind the model from Python->JS. """

        for trait_name in traits:
            model.on_trait_change(self._on_model_trait_changed, trait_name)
            value = getattr(model, trait_name)
            if isinstance(value, list):
                model.on_trait_change(self._on_model_list_items_changed,
                                      trait_name + '_items')

        return

    def _create_widget(self):
        """ Create the HTML widget that we use to render the view. """

        hosts = {
            'resources.jigna': JinjaRenderer(
                package       = 'jigna',
                template_root = 'resources'
            )
        }

        widget = HTMLWidget(
            callbacks        = [
                ('set_trait', self._bridge_set_trait),
                ('get_trait', self._bridge_get_trait),
                ('get_trait_info', self._bridge_get_trait_info)
            ],
            python_namespace = "python_bridge",
            hosts            = hosts,
            open_externally  = True,
            debug            = True
        )
        widget.create()

        return widget

    def _add_model(self, model, model_name):

        ADD_MODEL_TO_JS_TEMPLATE = """
            jigna.proxy_manager.add_model('${model_name}', '${id}');
        """

        js = Template(ADD_MODEL_TO_JS_TEMPLATE).render(
            model_name = model_name,
            id         = id(model),
        )

        self._widget.execute_js(js)

    def _generate_html(self, model, traits):
        
        document_html_template = Template(DOCUMENT_HTML_TEMPLATE)
        document_html = document_html_template.render(
            jquery        = 'http://resources.jigna/js/jquery.min.js',
            angular       = 'http://resources.jigna/js/angular.min.js',
            jigna         = 'http://resources.jigna/js/jigna.js',
            body_html     = self.html
        )

        return document_html

    def _get_trait_info(self, model, traits=None):
        """Return a dictionary of traits along with information on the trait.
        """
        if traits is None:
            traits = model.editable_traits()

        info = {}
        for trait_name in traits:
            value = getattr(model, trait_name)
            if isinstance(value, HasTraits):
                value_id = str(id(value))
                info[trait_name] = dict(type='instance', id=value_id)
                self._id_to_object_map[value_id] = value
            elif isinstance(value, list):
                trait = model.trait(trait_name)
                info[trait_name] = self._get_list_trait_info(value, trait)
            else:
                info[trait_name] = dict(type='primitive',
                                        value=json.dumps(value))
        return info

    def _get_list_trait_info(self, lst, trait):
        if isinstance(trait.inner_traits[0].trait_type,
                      (TraitInstance, Instance)):
            obj_ids = []
            for obj in lst:
                obj_id = str(id(obj))
                self._id_to_object_map.setdefault(obj_id, obj)
                obj_ids.append(obj_id)
            data = dict(type='list_instance', value=json.dumps(obj_ids))
        else:
            data = dict(type='list_primitive', value=json.dumps(lst))
        return data

    def _bridge_get_trait_info(self, id):
        model = self._id_to_object_map.get(id)
        self._bind_python_to_js(model, model.editable_traits())
        return json.dumps(self._get_trait_info(model))

    def _bridge_set_trait(self, id, trait_name, value_json):
        """ Set a trait on the model. """
        print "Python set_trait called", id, trait_name, value_json
        model = self._id_to_object_map.get(id)
        value = json.loads(value_json)
        setattr(model, trait_name, value)

        return

    def _bridge_get_trait(self, obj_id, trait_name):
        print "Python get_trait called,", obj_id, trait_name
        model = self._id_to_object_map.get(obj_id)
        value = getattr(model, trait_name)
        trait = model.trait(trait_name)
        if (isinstance(value, list) and
            isinstance(trait.inner_traits[0].trait_type,
                      (TraitInstance, Instance))):
            result = json.dumps([str(id(x)) for x in value])
        else:
            result = json.dumps(value)
        return result


    #### Trait change handlers ################################################

    def _on_model_trait_changed(self, model, trait_name, old, new):
        """ Called when any trait on the model has been changed. """
        if isinstance(new, HasTraits):
            value = str(id(new))
            self._id_to_object_map[value] = new
        elif isinstance(new, list):
            data = self._get_list_trait_info(new, model.trait(trait_name))
            value = data['value']
        else:
            value = json.dumps(new)

        ON_TRAIT_CHANGE_JS = """
        jigna.proxy_manager.on_trait_change('${id}', '${trait_name}', ${value});
        """

        js = Template(ON_TRAIT_CHANGE_JS).render(
            id  = str(id(model)),
            trait_name = trait_name,
            value = value
        )

        self._widget.execute_js(js)

        return

    def _on_model_list_items_changed(self, model, trait_items_name, old, new):
        """ Called when any trait on the model has been changed. """

        trait_name = trait_items_name[:-6]

        for x in new.added:
            self._id_to_object_map.setdefault(str(id(x)), x)

        #splice_args = [new.index, len(new.removed)] + new.added
        #value = json.dumps(splice_args)
        value = "null"

        on_list_items_change_js = """
        jigna.proxy_manager.on_list_items_change('${id}', '${trait_name}', ${value});
        """

        js = Template(on_list_items_change_js).render(
            id  = str(id(model)),
            trait_name = trait_name,
            value = value
        )

        self._widget.execute_js(js)

        return

#### EOF ######################################################################
