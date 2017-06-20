function viewPhoto(filename) {
    $('#chooselocationp').css("visibility", "hidden");
    $cam = $('#camera');
    $cam.find('img').attr("src", "/image/" + filename);
    $cam.find('a').attr("href", "/image/"+filename);
}

function removeDuplicates(arr) {
    function thingsEqual(thing1, thing2) {
        return thing1.x === thing2.x && thing1.y === thing2.y;
    }
    function arrayContains(arr, val) {
        var i = arr.length;
        while (i--) {
            if (thingsEqual(arr[i], val) ) {
                return true;
            }
        }
        return false;
    }
    var originalArr = arr.slice(0);
    var i, len, val;
    arr.length = 0;
    for (i = 0, len = originalArr.length; i < len; ++i) {
        val = originalArr[i];
        if (!arrayContains(arr, val)) {
            arr.push(val);
        }
    }
}

var tessellate = function(vList) {
    var indices = [];
    var currentIndice = 0;
    // array contour is used to triangulate the polygon
    var contours = [];
    vList.forEach(function(v) {
        contours.push({x:v.x, y:v.y, indice:currentIndice++});
    });
    // Triangulate
    var swctx = new poly2tri.SweepContext(contours);
    swctx.triangulate();
    // retrieve indices
    var triangles = swctx.getTriangles();
    triangles.forEach(function(t) {
        t.getPoints().forEach(function(p) {
            indices.push(p.indice);
        });
    });
    return indices;
};