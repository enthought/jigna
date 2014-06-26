// find the caption element
var element = document.getElementById('caption');

// add the 'green' class on mouseover...
element.addEventListener('mouseover', function(){
    element.className = 'green';
});

// ... and 'red' on mouseout
element.addEventListener('mouseout', function(){
    element.className = 'red';
});
