"""
This example shows that the jigna HTML view supports CSS 3D transforms, a
property of the underlying QGraphicsWebView item.

Card flip CSS source: http://desandro.github.io/3dtransforms/docs/card-flip.html
"""

#### Imports ####

from jigna.api import HTMLWidget, Template
from jigna.qt import QtGui
from traits.api import HasTraits, Enum

#### Domain model ####

class Card(HasTraits):
    visible_face = Enum('front', 'back')

    def flip(self):
        if self.visible_face == 'front':
            self.visible_face = 'back'

        else:
            self.visible_face = 'front'


#### UI layer ####

body_html = """
    <div class="container">
      <div id="card"
           ng-class="{ flipped: card.visible_face == 'back' }">
        <div class="front face">Front face</div>
        <div class="back face">Back face</div>
      </div>
    </div>

    <button ng-click='card.flip()'>
        Flip card
    </button>

    <style>
        .container {
            width: 200px;
            height: 260px;
            position: relative;
            -webkit-perspective: 800px;
        }

        #card {
          width: 100%;
          height: 100%;
          position: absolute;
          -webkit-transform-style: preserve-3d;
          -webkit-transition: -webkit-transform 1s;
        }

        #card .face {
          display: block;
          position: absolute;
          width: 100%;
          height: 100%;
          color: white;
          font-size: 16px;
          -webkit-backface-visibility: hidden;
        }

        #card .front {
          background: red;
        }

        #card .back {
          background: blue;
          -webkit-transform: rotateY( 180deg );
        }

        #card.flipped {
          -webkit-transform: rotateY( 180deg );
        }
    </style>
"""

template = Template(body_html=body_html)

#### Entry point ####

def main():
    # Start a QtGui application
    app = QtGui.QApplication([])

    # Instantiate the domain model
    card = Card()

    # Create a jigna based HTML widget to render the HTML template with the
    # given context.
    widget = HTMLWidget(
        template=template, context={'card': card}
    )
    widget.show()

    # Start the event loop
    app.exec_()

if __name__ == "__main__":
    main()

#### EOF ######################################################################
