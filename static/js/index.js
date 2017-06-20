window.addEventListener('DOMContentLoaded', function () {
    var canvas = document.getElementById('renderCanvas');
    var engine = new BABYLON.Engine(canvas, true);

    function loadMap(drone) {
        $("p#alert").text("Načítám mapu...");
        $("#loading").css("display", "block");
        $("#optionsbtns").css("visibility", "hidden");
        $("#dronesbtns").css("visibility", "hidden");

        $.getJSON('/lastflight/' + drone.toString(), function(lastflight) {
            if (lastflight["results"].length > 0) {
                htmlDronePath(lastflight["results"][0]["Id_flight"]);
                var arr = [];
                for (var i=0; i < lastflight["results"].length; i++) {
                    arr[i] = [lastflight["results"][i]["Longitude"], lastflight["results"][i]["Latitude"]];
                }
                $.ajax({
                    type: "POST",
                    url: "/gpstosjtsk",
                    data: JSON.stringify(arr),
                    dataType: "json",
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    success: function(sjtsk, _) {
                        sjtsk = JSON.parse(sjtsk["results"]);
                        var drone_path = [];
                        for (var i=0; i < lastflight["results"].length; i++) {
                            drone_path[i] = [sjtsk[i][0], sjtsk[i][1], lastflight["results"][i]["Height"]]
                        }

                        $.getJSON('/getmap/' + lastflight["results"][lastflight["results"].length-1]["Longitude"]
                            + "/" + lastflight["results"][lastflight["results"].length-1]["Latitude"], function(jsn) {
                            threeDScene(jsn, engine, canvas, drone_path);
                        });
                    }});
            } else {
                htmlDronePath(null);
                $("#alert").text("V databázi se nenachází žádný let (popř. jízda) tohoto zařízení nebo toto zařízení právě odstartovalo a nenahlásilo ještě svou pozici.");
                engine.stopRenderLoop();
                $("canvas").css("display", "none");
                $("#loading").css("display", "none");
                $("#optionsbtns").css("visibility", "visible");
                $("#dronesbtns").css("visibility", "visible");
            }
        });
    }


    function htmlPhotoChoices() {
        $.ajax("/dronephotos/" + $('#dronesbtns').find('input:radio:checked').val())
            .done(function(html) {
                $("#photochoices").html(html);
            }
        );
    }

    function htmlDronePath(flight) {
        if (flight) {
            $.ajax("/dronepath/" + flight.toString())
                .done(function (html) {
                    $("#dronepath").html(html);
                }
            );
        } else {
            $("#dronepath").html("");
        }
    }

    function camera() {  // chci kameru
        if (this.value == "camera") {
            $("#instructions").css("display", "none");
            $("#alert").text("");
            $("canvas").css("display", "none");
            engine.stopRenderLoop();
            $('#camera').css("display", "block");
            htmlPhotoChoices();
            htmlDronePath(null);
        }
    }

    function map() {  // chci mapu
        if (this.value == "map") {
            $("#instructions").css("display", "block");
            //$("canvas").css("display", "inline-block");
            loadMap($('#dronesbtns').find('input:radio:checked').val());
            $('#camera').css("display", "none");
            $("#photochoices").html("");
        }
    }

    $('#camera').css("display", "none");
    $("#camerabtn").change(camera);
    $("#mapbtn").change(map);

    function droneChange() {  // zmenil se dron
        if ($('#optionsbtns').find('input:radio:checked').val() == "map") {  // je vybrana mapa
            loadMap(this.value);
        } else {  // je vybrana kamera
            htmlPhotoChoices();
            $('#chooselocationp').css("visibility", "visible");
            $('#camera').find('img').attr("src", "");
        }
    }

    $("input[name=drones]").change(droneChange);

    loadMap($('#dronesbtns').find('input:radio:checked').val());
});

