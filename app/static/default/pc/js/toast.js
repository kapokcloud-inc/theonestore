function Toast(msg){
  var m = document.createElement('div');
  m.innerHTML = msg;
  m.style.cssText="max-width:60%;min-width: 150px;padding:0 20px;height: 60px;color: rgb(255, 255, 255);line-height: 60px;text-align: center;border-radius: 4px;position: fixed;top: 30%;left: 50%;transform: translate(-50%, 0%);z-index: 999999;background: rgba(0, 0, 0,.7);font-size: 16px;";
  document.body.appendChild(m);
  setTimeout(function() {
    // var d = 0.5;
    // m.style.webkitTransition = '-webkit-transform ' + d + 's ease-in, opacity ' + d + 's ease-in';
    m.style.opacity = '0';
    setTimeout(function() { 
      document.body.removeChild(m) 
    }, 300);
  }, 300);
}