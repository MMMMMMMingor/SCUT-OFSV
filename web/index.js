const videoElement = document.getElementsByClassName("input_video")[0];
const canvasElement = document.getElementById("real_canvas");
const fakeCanvasElement = document.getElementById("fake_canvas");
const finishBtn = document.getElementById("finish_btn");
const clearBtn = document.getElementById("clear_btn");
const controlsElement = document.getElementsByClassName(
    "control-panel"
)[0];
const canvasCtx = canvasElement.getContext("2d");
const fakeCanvasCtx = fakeCanvasElement.getContext("2d");

canvasCtx.strokeStyle = "#00ff00";
canvasCtx.lineWidth = 3;

fakeCanvasCtx.fillStyle = "#ff0000";

var data = [];

// We'll add this to our control panel later, but we'll save it here so we can
// call tick() each time the graph runs.
const fpsControl = new FPS();

// Optimization: Turn off animated spinner after its hiding animation is done.
const spinner = document.querySelector(".loading");

navigator.getUserMedia = navigator.getUserMedia ||
    navigator.webkitGetUserMedia || navigator.mozGetUserMedia;

spinner.ontransitionend = () => {
    spinner.style.display = "none";
};

document.addEventListener("keydown", (event) => {
    if (event.key == "c") {
        clearBtn.click();
    }
    if (event.key == "f") {
        finishBtn.click();
    }
});

finishBtn.addEventListener("click", () => {
    alert(data.length);
});

clearBtn.addEventListener("click", () => {
    data = [];
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
});

function __abs(num) {
    if (num < 0) {
        return -1 * num
    }

    return num;
}

function closeEnough(finger1, finger2, factor) {
    if (__abs(finger1.x - finger2.x) < factor
        && __abs(finger1.y - finger2.y) < factor
        && __abs(finger1.z - finger2.z) < factor) {
        return true;
    }
    return false;
}

function drawLandmarks(ctx, last, cur) {
    if (last == undefined || last == null) {
        return;
    }

    ctx.beginPath();
    ctx.moveTo(canvasElement.width * last.x, canvasElement.height * last.y);
    ctx.lineTo(canvasElement.width * cur.x, canvasElement.height * cur.y);
    ctx.closePath();
    ctx.stroke();
}

function drawPoints(ctx, points) {
    for (p of points) {
        let x = canvasElement.width * p.x;
        let y = canvasElement.height * p.y;
        let r = 4;

        ctx.beginPath();
        ctx.arc(x, y, r, 0, 2 * Math.PI);
        ctx.fill();
    }
}

function onResults(results) {
    // Update the frame rate.
    fpsControl.tick();

    // Draw the overlays.
    canvasCtx.save();

    fakeCanvasCtx.clearRect(0, 0, fakeCanvasElement.width, fakeCanvasElement.height);

    if (results.multiHandLandmarks && results.multiHandedness) {
        for (let landmarks of results.multiHandLandmarks) {
            // Hide the spinner.
            document.body.classList.add("loaded");

            var thumb = landmarks[4];
            var index_finger = landmarks[8]

            if (closeEnough(thumb, index_finger, 0.06)) {
                // drawLandmarks(canvasCtx, [thumb], {
                //     color: "#00FF00",
                //     radius: 1,
                //     lineWidth: 1,
                // });
                drawLandmarks(canvasCtx, data[data.length - 1], thumb);
                data.push(thumb);
            } else {
                // drawLandmarks(fakeCanvasCtx, [thumb, index_finger], {
                //     color: "#FF0000",
                //     radius: 1,
                // });
                drawPoints(fakeCanvasCtx, [thumb, index_finger]);
                data.push(null);
            }
        }
    }
    canvasCtx.restore();
}

const hands = new Hands({
    locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.1/${file}`;
    },
});
hands.onResults(onResults);

/**
 * Instantiate a camera. We'll feed each frame we receive into the solution.
 */
const camera = new Camera(videoElement, {
    onFrame: async () => {
        // fpsControl.tick();
        await hands.send({ image: videoElement });
    }
});
camera.start();

// Present a control panel through which the user can manipulate the solution
// options.
new ControlPanel(controlsElement, {
    maxNumHands: 1,
    minDetectionConfidence: 0.85,
    minTrackingConfidence: 0.65,
}).add([
    new StaticText({ title: "online air signature demo" }),
    fpsControl,
    // new Slider({
    //     title: "Max Number of finger",
    //     field: "maxNumHands",
    //     range: [1, 4],
    //     step: 1,
    // }),
    // new Slider({
    //     title: "Min Detection Confidence",
    //     field: "minDetectionConfidence",
    //     range: [0, 1],
    //     step: 0.01,
    // }),
    // new Slider({
    //     title: "Min Tracking Confidence",
    //     field: "minTrackingConfidence",
    //     range: [0, 1],
    //     step: 0.01,
    // }),
]).on((options) => {
    hands.setOptions(options);
});