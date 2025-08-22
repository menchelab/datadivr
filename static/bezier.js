function draw() {
    //clear canvas
    ctx.clearRect(0, 0, c.width, c.height);
    drawCircles();
    bezier = function(t, p0, p1, p2, p3){
      var cX = 3 * (p1.x - p0.x),
          bX = 3 * (p2.x - p1.x) - cX,
          aX = p3.x - p0.x - cX - bX;
            
      var cY = 3 * (p1.y - p0.y),
          bY = 3 * (p2.y - p1.y) - cY,
          aY = p3.y - p0.y - cY - bY;
            
      var x = (aX * Math.pow(t, 3)) + (bX * Math.pow(t, 2)) + (cX * t) + p0.x;
      var y = (aY * Math.pow(t, 3)) + (bY * Math.pow(t, 2)) + (cY * t) + p0.y;
            
      return {x: x, y: y};
    },

    (function(){
      var accuracy = 0.01, //this'll give the bezier 100 segments
        
          p0 = {x: c1.x, y: c1.y}, //use whatever points you want obviously
          p1 = {x: c2.x, y: c2.y},
          p2 = {x: c3.x, y: c3.y},
          p3 = {x: c4.x, y: c4.y},
          //reference to the canvas element

//reference to 2d context

          ctx = parent.getContext('2d');

            //ctx.width = 400;
            //ctx.height = 200;
            //document.body.appendChild(ctx.canvas);
            
            ctx.moveTo(p0.x, p0.y);
            for (var i=0; i<1; i+=accuracy){
                var p = bezier(i, p0, p1, p2, p3);
                ctx.lineTo(p.x, p.y);
            }
  
      ctx.stroke()
    })()


}

//draw circles
function drawCircles() {
    for (var i = circles.length - 1; i >= 0; i--) {
        circles[i].draw();
    }
}

//key track of circle focus and focused index
var focused = {
   key: 0,
   state: false
}

//circle Object
function Circle(x, y, r, fill, stroke) {
    this.startingAngle = 0;
    this.endAngle = 2 * Math.PI;
    this.x = x;
    this.y = y;
    this.r = r;

    this.fill = fill;
    this.stroke = stroke;

    this.draw = function () {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.r, this.startingAngle, this.endAngle);
        ctx.fillStyle = this.fill;
        ctx.lineWidth = 3;
        ctx.fill();
        ctx.strokeStyle = this.stroke;
        ctx.stroke();
    }
}

function move(e) {
    if (!isMouseDown) {
        return;
    }
    getMousePosition(e);
    //if any circle is focused
    if (focused.state) {
        //if (circles[focused.key]["fill"] == "blue"){
        //circles[focused.key].y = mousePosition.y;
       // c1.y = mousePosition.y;  
        //}
        //else{
        circles[focused.key].x = mousePosition.x;
        circles[focused.key].y = mousePosition.y; 
        //}

        draw();
        //console.log(focused.key)
        return;
    }
    //no circle currently focused check if circle is hovered
    for (var i = 0; i < circles.length; i++) {
        if (intersects(circles[i])) {
            circles.move(i, 0);
            focused.state = true;
            break;
        }
    }
    draw();
    var p0 = [c1.x,c1.y]; //use whatever points you want obviously
    var p1 = [c2.x,c2.y];
    var p2 = [c3.x,c3.y];
    var p3 = [c4.x,c4.y];
    var LUT_x = [], LUT_y = [], t, a, b, c, d;
    for(let i=0; i<100; i++) {
    t = i/100;
    a = (1-t)*(1-t)*(1-t);
    b = (1-t)*(1-t)*t;
    c = (1-t)*t*t;
    d = t*t*t;
    LUT_x.push( a*p0[0] + 3*b*p1[0] + 3*c*p2[0] + d*p3[0] );
    LUT_y.push( a*p0[1] + 3*b*p1[1] + 3*c*p2[1] + d*p3[1] );
    }
    console.log(p0[0]);
    console.log(LUT_y);
}

//set mousedown state
function setDraggable(e) {
    var t = e.type;
    if (t === "mousedown") {
        isMouseDown = true;
    } else if (t === "mouseup") {
        isMouseDown = false;
        releaseFocus();
    }
}

function releaseFocus() {
    focused.state = false;
}

function getMousePosition(e) {
    var rect = c.getBoundingClientRect();
    mousePosition = {
        x: Math.round(e.x - rect.left),
        y: Math.round(e.y - rect.top)
    }
}

//detects whether the mouse cursor is between x and y relative to the radius specified
function intersects(circle) {
    // subtract the x, y coordinates from the mouse position to get coordinates 
    // for the hotspot location and check against the area of the radius
    var areaX = mousePosition.x - circle.x;
    var areaY = mousePosition.y - circle.y;
    //return true if x^2 + y^2 <= radius squared.
    return areaX * areaX + areaY * areaY <= circle.r * circle.r;
}