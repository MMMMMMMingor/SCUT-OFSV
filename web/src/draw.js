const canvasElement = document.getElementById("real_canvas");

function __abs(num) {
    if (num < 0) {
        return -1 * num
    }

    return num;
}

export function closeEnough(finger1, finger2, factor) {
    if (__abs(finger1.x - finger2.x) < factor
        && __abs(finger1.y - finger2.y) < factor
        && __abs(finger1.z - finger2.z) < factor) {
        return true;
    }
    return false;
}

export function drawLandmarks(ctx, last, cur) {
    if (last == undefined || last == null) {
        return;
    }

    ctx.beginPath();
    ctx.moveTo(canvasElement.width * last.x, canvasElement.height * last.y);
    ctx.lineTo(canvasElement.width * cur.x, canvasElement.height * cur.y);
    ctx.closePath();
    ctx.stroke();
}

export function drawPoints(ctx, points) {
    for (const p of points) {
        let x = canvasElement.width * p.x;
        let y = canvasElement.height * p.y;
        let r = 4;

        ctx.beginPath();
        ctx.arc(x, y, r, 0, 2 * Math.PI);
        ctx.fill();
    }
}