(function(window){var svgSprite='<svg><symbol id="icon-cancel" viewBox="0 0 1024 1024"><path d="M556.097 512l219.075-219.075c12.177-12.177 12.177-31.92 0-44.097-12.178-12.177-31.92-12.177-44.098 0L512 467.903 292.925 248.828c-12.177-12.177-31.92-12.177-44.097 0s-12.177 31.92 0 44.097L467.903 512 248.828 731.074c-12.177 12.178-12.177 31.92 0 44.098 12.177 12.176 31.92 12.176 44.097 0L512 556.097l219.075 219.076c6.089 6.088 14.069 9.132 22.049 9.132s15.96-3.044 22.048-9.132c12.178-12.178 12.178-31.92 0.001-44.097L556.097 512z" fill="" ></path></symbol><symbol id="icon-dagou" viewBox="0 0 1024 1024"><path d="M388.849704 864.136036c-13.430894 0-26.864858-5.126764-37.114293-15.372106L23.658328 520.685823c-20.499893-20.496823-20.499893-53.732785 0-74.230632 20.497846-20.499893 53.730739-20.499893 74.230632 0l290.959721 290.959721L925.865447 200.397123c20.499893-20.497846 53.731762-20.497846 74.231655 0 20.497846 20.49887 20.497846 53.732785 0 74.231655L425.966043 848.76393C415.716608 859.010295 402.283668 864.136036 388.849704 864.136036L388.849704 864.136036z"  ></path></symbol></svg>';var script=function(){var scripts=document.getElementsByTagName("script");return scripts[scripts.length-1]}();var shouldInjectCss=script.getAttribute("data-injectcss");var ready=function(fn){if(document.addEventListener){if(~["complete","loaded","interactive"].indexOf(document.readyState)){setTimeout(fn,0)}else{var loadFn=function(){document.removeEventListener("DOMContentLoaded",loadFn,false);fn()};document.addEventListener("DOMContentLoaded",loadFn,false)}}else if(document.attachEvent){IEContentLoaded(window,fn)}function IEContentLoaded(w,fn){var d=w.document,done=false,init=function(){if(!done){done=true;fn()}};var polling=function(){try{d.documentElement.doScroll("left")}catch(e){setTimeout(polling,50);return}init()};polling();d.onreadystatechange=function(){if(d.readyState=="complete"){d.onreadystatechange=null;init()}}}};var before=function(el,target){target.parentNode.insertBefore(el,target)};var prepend=function(el,target){if(target.firstChild){before(el,target.firstChild)}else{target.appendChild(el)}};function appendSvg(){var div,svg;div=document.createElement("div");div.innerHTML=svgSprite;svgSprite=null;svg=div.getElementsByTagName("svg")[0];if(svg){svg.setAttribute("aria-hidden","true");svg.style.position="absolute";svg.style.width=0;svg.style.height=0;svg.style.overflow="hidden";prepend(svg,document.body)}}if(shouldInjectCss&&!window.__iconfont__svg__cssinject__){window.__iconfont__svg__cssinject__=true;try{document.write("<style>.svgfont {display: inline-block;width: 1em;height: 1em;fill: currentColor;vertical-align: -0.1em;font-size:16px;}</style>")}catch(e){console&&console.log(e)}}ready(appendSvg)})(window)