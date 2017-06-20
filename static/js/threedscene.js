function threeDScene(jsn, engine, canvas, drone_path) {
    jsn = JSON.parse(jsn["results"]);
    var xzero = jsn["tiles"][0]["x"];
    var yzero = jsn["tiles"][0]["y"];
    var zzero = jsn["tiles"][0]["zMin"];
    var dmr = jsn["tiles"];
    var step = jsn["tiles"][0]["step"];
    var size = jsn["tiles"][0]["size"];
    var entities = jsn["entities"];

    // create a basic BJS Scene object
    var scene = new BABYLON.Scene(engine);

    function camera_light() {
        // create an ArcRotateCamera
        var camera = new BABYLON.ArcRotateCamera("ArcRotateCamera", 0, 0, 10, new BABYLON.Vector3(0, 0, 0), scene);
        camera.lowerRadiusLimit = 1;
        camera.upperRadiusLimit = 500;
        camera.upperAlphaLimit = 2.5;
        camera.lowerAlphaLimit = 0.2;
        camera.upperBetaLimit = 3.0;
        camera.lowerBetaLimit = 0.6;
        // target the camera
        camera.setTarget(new BABYLON.Vector3(- size / step * 1.5, - size / step * 1.5, 0));
        camera.radius = 200;  // default zoom
        // attach the camera to the canvas
        camera.attachControl(canvas);
        camera.alpha += 1.4;
        camera.beta += 1.3;

        // create a basic light
        var light = new BABYLON.HemisphericLight('light1', new BABYLON.Vector3(0, -1, 1), scene);
        /*scene.registerBeforeRender(function () {
            light.position = camera.position;
        });*/
    }

    function makeTextPlane(text, color, size) {
        var dynamicTexture = new BABYLON.DynamicTexture("DynamicTexture", 50, scene, true);
        dynamicTexture.hasAlpha = true;
        dynamicTexture.drawText(text, 10, 40, "bold 10px Arial", color, "transparent", true);
        var plane = new BABYLON.Mesh.CreatePlane("TextPlane", size, scene, true);
        plane.material = new BABYLON.StandardMaterial("TextPlaneMaterial", scene);
        plane.material.backFaceCulling = false;
        plane.material.specularColor = new BABYLON.Color3(0, 0, 0);
        plane.material.diffuseTexture = dynamicTexture;
        return plane;
    }

    function showAxis(size) {
        var axisX = BABYLON.Mesh.CreateLines("axisX", [
            new BABYLON.Vector3.Zero(), new BABYLON.Vector3(size, 0, 0), new BABYLON.Vector3(size * 0.95, 0.05 * size, 0),
            new BABYLON.Vector3(size, 0, 0), new BABYLON.Vector3(size * 0.95, -0.05 * size, 0)
        ], scene);
        axisX.color = new BABYLON.Color3(1, 0, 0);
        var xChar = makeTextPlane("X", "red", size);
        xChar.position = new BABYLON.Vector3(0.9 * size, -0.05 * size, 0);
        var axisY = BABYLON.Mesh.CreateLines("axisY", [
            new BABYLON.Vector3.Zero(), new BABYLON.Vector3(0, size, 0), new BABYLON.Vector3(-0.05 * size, size * 0.95, 0),
            new BABYLON.Vector3(0, size, 0), new BABYLON.Vector3(0.05 * size, size * 0.95, 0)
        ], scene);
        axisY.color = new BABYLON.Color3(0, 1, 0);
        var yChar = makeTextPlane("Y", "green", size);
        yChar.position = new BABYLON.Vector3(0, 0.9 * size, -0.05 * size);
        var axisZ = BABYLON.Mesh.CreateLines("axisZ", [
            new BABYLON.Vector3.Zero(), new BABYLON.Vector3(0, 0, size), new BABYLON.Vector3(0, -0.05 * size, size * 0.95),
            new BABYLON.Vector3(0, 0, size), new BABYLON.Vector3(0, 0.05 * size, size * 0.95)
        ], scene);
        axisZ.color = new BABYLON.Color3(0, 0, 1);
        var zChar = makeTextPlane("Z", "blue", size);
        zChar.position = new BABYLON.Vector3(0, 0.05 * size, 0.9 * size);
    }

    function ground() {
        for (var tile = 0; tile < dmr.length; tile++) {
            var texture = dmr[tile]["texture"];
            var materialGround = new BABYLON.StandardMaterial("texture1", scene);
            materialGround.diffuseTexture = BABYLON.Texture.CreateFromBase64String("data:image/jpg;base64," + texture,
                "texture" + tile.toString(), scene);
            materialGround.diffuseTexture.uAng = Math.PI;
            materialGround.specularColor = new BABYLON.Color3(0, 0, 0);

            paths = [];
            for (var i = 0; i < dmr[tile]["dataDMR"].length; i++) {
                var path = [];
                for (var j = 0; j < dmr[tile]["dataDMR"][i].length; j++) {
                    path[j] = new BABYLON.Vector3(i + (yzero - dmr[tile]["y"]) / step,
                        -j + (xzero - dmr[tile]["x"]) / step,
                        (dmr[tile]["dataDMR"][i][j] - zzero) / step);
                }
                paths[i] = path;
            }

            var ribbon = new BABYLON.Mesh.CreateRibbon("ribbon" + tile.toString(), paths, false, false, null,
                scene, false, BABYLON.Mesh.DOUBLESIDE);
            ribbon.material = materialGround;
            ribbon.rotation.x = Math.PI;
            ribbon.rotation.y = Math.PI;
            ribbon.rotation.z = Math.PI / 2;
        }
    }

    function buildings() {
        entities.forEach(function (entity) {
            if (entity["type"] != "building") return;  // vykresovat pouze budovy
            var origminz = entity["minZ"];
            var origmaxz = entity["maxZ"];
            var height = (origmaxz - origminz) / step;
            var floorz = (origminz - zzero) / step;
            var roofz = floorz + height;
            var shape = [];
            for (i = 0; i < entity["SJTSK"].length; i++) {
                shape[i] = new BABYLON.Vector3(-(entity["SJTSK"][i][0] - xzero) / step,
                    (entity["SJTSK"][i][1] - yzero) / step, floorz);
            }
            //_ = BABYLON.Mesh.CreateLines("sl" + entity["id"], shape, scene);

            function displayEntityId() {
                var description = makeTextPlane(entity["id"], "red", 4);
                description.position = new BABYLON.Vector3(shape[0].x, shape[0].y, roofz);
                description.position.z += 1;
                description.rotation.y = Math.PI;
            }

            function createWalls() {
                var extrudepath = [
                    new BABYLON.Vector3(0, 0, 0),
                    new BABYLON.Vector3(0, 0, height)
                ];
                _ = BABYLON.Mesh.ExtrudeShape("extruded" + entity["id"], shape, extrudepath, 1, 0,
                    BABYLON.Mesh.NO_CAP, scene, false, BABYLON.Mesh.DOUBLESIDE);
            }

            function createFloorRoof() {
                //for (i = 0; i < shape.length - 1; i++) {
                //    shape[i] = new BABYLON.Vector2(shape[i].x, shape[i].y);
                //}
                removeDuplicates(shape);
                var indices = tessellate(shape);
                //Create a cap mesh
                var floor = new BABYLON.Mesh("cap" + entity["id"], scene);  // podlaha
                var roof = new BABYLON.Mesh("capback" + entity["id"], scene);  // strecha
                //Create a vertexData object
                var vertexData = new BABYLON.VertexData();
                var vertexDataBack = new BABYLON.VertexData();
                //Assign positions and indices to vertexData
                var positions = [];
                for (i = 0; i < shape.length; i++) {
                    positions.push(shape[i].x, shape[i].y, 0);
                }
                var revIndices = Array.from(indices);
                revIndices.reverse();
                vertexData.positions = positions;
                vertexData.indices = indices;
                vertexDataBack.positions = positions;
                vertexDataBack.indices = revIndices;
                //Apply vertexData to custom mesh
                vertexData.applyToMesh(floor);
                vertexDataBack.applyToMesh(roof);
                floor.position.z = floorz;  // podlaha
                roof.position.z = roofz;  // strecha
                var material = new BABYLON.StandardMaterial("texture1", scene);
                floor.material = material;
                roof.material = material;
            }

            //displayEntityId();
            createWalls();
            createFloorRoof();
        });
    }

    function path_curve(path) {
        var points = [];  // an array of Vector3 the curve must pass through : the control points
        for (var i = 0; i < path.length; i++) {
            points[i] = new BABYLON.Vector3(-(path[i][0] - xzero) / step, (path[i][1] - yzero) / step,
                (path[i][2] - zzero) / step);
        }
        var lines = BABYLON.MeshBuilder.CreateLines("path", {"points": points}, scene);
        lines.color = new BABYLON.Color3(0, 1, 0);
        start_text = makeTextPlane("START", "red", 10);
        start_text.position = points[0];
        start_text.position.z += 1;
        start_text.rotation.y = Math.PI;
    }

    function renderLoop() {
        scene.render();
    }

    window.addEventListener('resize', function () {
        engine.resize();
    });
    camera_light();
    //showAxis(20);
    ground();
    buildings();
    path_curve(drone_path);
    engine.runRenderLoop(renderLoop);

    $("canvas").css("display", "inline-block");
    $("#alert").text("");
    $("#loading").css("display", "none");
    $("#optionsbtns").css("visibility", "visible");
    $("#dronesbtns").css("visibility", "visible");
}