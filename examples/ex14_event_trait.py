"""
This example demonstrates Jigna's ability to respond to `Event` trait firings.
"""

#### Imports ####

from traits.api import HasTraits, Str, Event, List
from jigna.api import HTMLWidget, Template
from jigna.qt import QtGui
import time

#### Domain model ####

class Downloader(HasTraits):

    file_urls = List(Str)
    file_downloaded = Event

    def download_files(self):
        """ Download the files specified by the file_urls. Fire a
        `file_downloaded` event with each file download. """

        for file_url in self.file_urls:
            # Simulate downloading the file
            time.sleep(1)

            # This will fire the `file_downloaded` event and make `file_url` as
            # the event payload
            self.file_downloaded = file_url

#### UI layer ####

body_html = """
    <div>
         <!-- Start the download of files in a thread -->
         <button ng-click="jigna.threaded(downloader, 'download_files')">
            Download files
         </button>

         <!-- Custom javascript to attach event handlers -->
         <script type='text/javascript'>

            // Show a "Download complete" dialog with every file download.
            var on_file_downloaded = function(event){
                var file_url = event.data.value;
                alert("Download complete: " + file_url);
            };

            // A proxy for the Python model `downloader` is available inside
            // jigna.models
            var downloader = jigna.models['downloader'];

            // Attach the event listener
            jigna.add_listener(downloader, 'file_downloaded', on_file_downloaded)

         </script>
    </div>
"""

template = Template(body_html=body_html)

#### Entry point ####

def main():
    # Start the Qt application
    app = QtGui.QApplication([])

    # Instantiate the domain model
    file_urls = ['images/lena.png', 'videos/big-buck-bunny.mp4']
    downloader = Downloader(file_urls=file_urls)

    # Create the jigna based HTML widget which renders the given HTML template
    # with the given context.
    widget = HTMLWidget(template=template, context={'downloader':downloader})
    widget.show()

    # Start the event loop.
    #
    # Clicking on the button in the UI will call the `download_files` method in
    # a thread. After each file is "downloaded", a Javascript alert should come
    # up. This is in response to a Python event on each file download.
    app.exec_()

if __name__ == "__main__":
    main()

#### EOF ######################################################################
