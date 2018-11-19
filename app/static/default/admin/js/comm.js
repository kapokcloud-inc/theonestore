/**
*    theonestore
*    https://github.com/kapokcloud-inc/theonestore
*    ~~~~~~~~~~~
*    
*    :copyright: © 2018 by the Kapokcloud Inc.
*    :license: BSD, see LICENSE for more details.
*
*    admin公共js函数
**/
$(document).ready(function () {
    //绑定input图片上传预览事件
    $('input[type=file][uploadtype=images]').change(function (e) { 
        e.preventDefault();
        previewFile(this);
    });
    
    // Switchery
    var elems = Array.prototype.slice.call(document.querySelectorAll('.js-switch'));
    $('.js-switch').each(function() {
      console.log( $(this).data())
      new Switchery($(this)[0], $(this).data());
    });

});

function previewFile(input) {
    // 判断浏览器是否支持文件读取操作
    if (!(window.File || window.FileReader || window.FileList || window.Blob)) {
        return;
    }

    var $input = $(input);
    var $div = $input.parent();
    var files = $input.prop('files');
    if (files.length == 0) {
        return;
    }
    var file = files[0];
    var $img = $div.find('a>img');
    var reader = new FileReader();
    reader.onloadend = function() {
        if ($img.length > 0) {
            $img.attr('src', reader.result);
            $img.parent().attr('href', 'javascript:;');
        } else {
            var img_html = '<a href="javascript:;"><img style="width:200px; padding-left:0px;" src="' + reader.result + '"></a>';
            $div.append(img_html);
        }
        
    }
    if (file) {
        reader.readAsDataURL(file);
    }
    
}
