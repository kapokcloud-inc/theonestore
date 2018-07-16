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
    $('input[type=file][file-type=image]').change(function (e) { 
        e.preventDefault();
        previewFile(this);
    });
});

function previewFile(input) {
    // 判断浏览器是否支持文件读取操作
    if (!(window.File || window.FileReader || window.FileList || window.Blob)) {
        return;
    }

    var $input = $(input);
    var files = $input.prop('files');
    if (files.length == 0) {
        return;
    }
    var file = files[0];
    var $img = $input.next().find('img');
    var reader = new FileReader();
    reader.onloadend = function() {
        $img.attr('src', reader.result);
    }
    if (file) {
        reader.readAsDataURL(file);
    }
    
}
