// A Horrible hack to update objects.  This was gleaned from the vuejs
// code.  The problem we have is that vuejs cannot listen to changes to
// model changes because we use getters/setters.  Internally vue uses an
// observer to notify dependent elements.  We use the __ob__ attribute
// to get the observer and call its `dep.notify()`, this makes
// everything work really well.
jigna.add_listener('jigna', 'object_changed', function (event) {
    var obj = event.object;
    if (obj && obj.__ob__) {
        obj.__ob__.dep.notify();
    }
});
