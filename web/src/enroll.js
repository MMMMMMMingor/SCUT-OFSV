import { Camera } from "@mediapipe/camera_utils/camera_utils";
import { FPS, ControlPanel, StaticText } from "@mediapipe/control_utils/control_utils";
import { Hands } from "@mediapipe/hands/hands";
import { closeEnough, drawLandmarks, drawPoints } from "./draw";
import "@mediapipe/control_utils/control_utils.css"
import "./index.css"
import axios from "axios";

navigator.getUserMedia = navigator.getUserMedia ||
    navigator.webkitGetUserMedia || navigator.mozGetUserMedia;

const params = new URLSearchParams(window.location.search);
const username = params.get("username");
if (!username) {
    window.location = '/';
}

const videoElement = document.getElementsByClassName("input_video")[0];
const canvasElement = document.getElementById("real_canvas");
const fakeCanvasElement = document.getElementById("fake_canvas");
const finishBtn = document.getElementById("finish_btn");
const clearBtn = document.getElementById("clear_btn");
const controlsElement = document.getElementById("control_panel");
const signatures_count = document.getElementById("signatures_count");
const signatureInvalid = document.getElementById('signature_invalid');
const canvasCtx = canvasElement.getContext("2d");
const fakeCanvasCtx = fakeCanvasElement.getContext("2d");
let has_loaded = false;

canvasCtx.strokeStyle = "#00ff00";
canvasCtx.lineWidth = 3;

fakeCanvasCtx.fillStyle = "#ff0000";

// We'll add this to our control panel later, but we'll save it here so we can
// call tick() each time the graph runs.
const fpsControl = new FPS();
let data = [];
let enrollment_signatures = [];

document.addEventListener("keydown", (event) => {
    if (event.key == "c") {
        clearBtn.click();
    }
    if (event.key == "f") {
        finishBtn.click();
    }
});

finishBtn.addEventListener("click", async (e) => {
    let signature_data = data.filter((p) => { return p !== null });
    signature_data = signature_data.map((p) => { return { ts:p.ts, x: p.x, y: p.y, z: p.z } });
    let new_signature_data = { ts:[], x: [], y: [], z: [] };
    for (let p of signature_data) {
        new_signature_data.ts.push(p.ts);
        new_signature_data.x.push(p.x);
        new_signature_data.y.push(p.y);
        new_signature_data.z.push(p.z);
    }
    console.log(new_signature_data);

    if (signature_data.length <= 10) {
        signatureInvalid.classList.toggle('hidden');

        setTimeout(() => {
            signatureInvalid.classList.toggle('hidden');
        }, 2500);

        return;
    }

    enrollment_signatures.push(new_signature_data);
    data = [];
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);

    let len = enrollment_signatures.length;
    signatures_count.innerHTML = `${len}/5`;

    if (len === 4) {
        finishBtn.innerText = 'Finish';
    }

    if (len === 5) {
        console.log(enrollment_signatures);
        document.body.classList.remove("loaded");
        await axios.post('/api/enrollment', {
            username: username,
            signatures: enrollment_signatures
        });
        let redirect_url = '/index.html?username=' + encodeURIComponent(username);
        window.location = redirect_url;
    }
});

clearBtn.addEventListener("click", () => {
    data = [];
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
});


function onResults(results) {
    // Update the frame rate.
    fpsControl.tick();

    // Hide the spinner.
    if (!has_loaded) {
        has_loaded = true;
        document.body.classList.add("loaded");
    }

    // Draw the overlays.
    canvasCtx.save();

    fakeCanvasCtx.clearRect(0, 0, fakeCanvasElement.width, fakeCanvasElement.height);

    if (results.multiHandLandmarks && results.multiHandedness) {
        for (let landmarks of results.multiHandLandmarks) {

            var thumb = landmarks[4];
            var index_finger = landmarks[8]

            if (closeEnough(thumb, index_finger, 0.06)) {
                drawLandmarks(canvasCtx, data[data.length - 1], thumb);
                data.push({ts: Date.now(), ...thumb});
            } else {
                drawPoints(fakeCanvasCtx, [thumb, index_finger]);
                if (data[data.length - 1] !== null) {
                    data.push(null);
                }
            }
        }
    }
    canvasCtx.restore();
}

const hands = new Hands({
    locateFile: (file) => {
        // return `https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.1/${file}`;
        return `https://cdn.firego.cn/model/${file}`;
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
    minTrackingConfidence: 0.75,
}).add([
    new StaticText({ title: "enrollment" }),
    fpsControl,
]).on((options) => {
    hands.setOptions(options);
});