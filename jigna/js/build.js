{
    "baseUrl": "src/",
    "name": "external/almond",
    "include": ["main"],
    "mainConfigFile": "src/main.js",
    "out": "dist/jigna.js",
    // wrapping the built file with some start code and end code. This is
    // done to make sure we have the jigna module available as a third party
    // library synchronously. Instructions followed from here:
    // https://github.com/jrburke/almond#exporting-a-public-api
    "wrap": {
        "startFile": "start_frag.js",
        "endFile": "end_frag.js"
    }
}
