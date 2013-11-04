from traits.api import HasTraits, Int, Str
from jigna.web import JignaWebView, serve

#### Domain model ####

class Person(HasTraits):
    name = Str
    age  = Int

#### UI layer ####

body_html = """
    <div>
      Name: <input ng-model="model.name">
      Age: <input ng-model="model.age" type='number'>
    </div>
"""

person_view = JignaWebView(body_html=body_html)

#### Entry point ####

def main():
    def listener(obj, traitname, old, new):
        print obj, traitname, old, new

    fred  = Person(name='Fred', age=42)
    fred.on_trait_change(listener)
    def update_fred():
        fred.name = "Wilma"
        fred.age = 4

    person_view.show(model=fred)
    serve(person_view, thread=True)
    fred.configure_traits()

if __name__ == "__main__":
    main()

#### EOF ######################################################################
