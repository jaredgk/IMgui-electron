/*global alert, $, jQuery, FileReader*/

function makeUrl() {
    console.log('hello');
    var canvas = document.getElementById("idcanvas");
    var ctx = canvas.getContext("2d");
    var data = "<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'>" +
        "<foreignObject width='100%' height='100%'>" + $("#tablediv").html() +
        "</foreignObject>" +
        "</svg>";
    var DOMURL = self.URL || self.webkitURL || self;
    var img = new Image();
    var svg = new Blob([data], {
        type: "image/svg+xml;charset=utf-8"
    });
    var url = DOMURL.createObjectURL(svg);
    img.onload = function() {
        ctx.drawImage(img, 0, 0);
        var a = document.createElement('a');
        a.download = "test.txt";
        a.href = canvas.toDataURL('image/png');
	//alert(a.href);
        document.body.appendChild(a);
        a.addEventListener("click", function(e) {
          a.parentNode.removeChild(a);
        });
        a.click();
    };
    img.src = url;
    console.log(url);
    
}

$('#pressbutton').click(function () {
    makeUrl();
                       
});