/**
 * 微信分享js
 */
$(document).ready(function () {
    $.get("/api/weixin/ticket", function(res){
        if (res.ret != 0) {
            $.toast(res.msg, "text");
            return;
        }

        var ticket = res.data.ticket;
        var appid = res.data.appid;

        wxShare(ticket, appid);

    });

});


/**
 * 微信分享
 * @param {*} ticket 
 * @param {*} appid 
 */
function wxShare(ticket, appid){
    var noncestr = Math.random().toString(36).substr(2, 15);
    var timestamp = parseInt(new Date().getTime() / 1000) + '';
    share_url = location.href.split('#')[0]; //当前地址

    var calcSignature = function (ticket, noncestr, ts, url) {
          var str = 'jsapi_ticket=' + ticket + '&noncestr=' + noncestr + '&timestamp='+ ts +'&url=' + url;
          console.log(str);
          var sign = hex_sha1(str);
          console.log(sign);
          return sign;
    }
    //生成微信所需要的签名
    signature = calcSignature(ticket, noncestr, timestamp, share_url);
    wxJssdk(appid, timestamp, noncestr, signature, share_url);
}


/**
 * 微信分享Api调用
 * @param {*} appid 
 * @param {*} timestamp 
 * @param {*} noncestr 
 * @param {*} signature 
 * @param {*} share_url 
 */
function wxJssdk(appid, timestamp, noncestr, signature, share_url){
    var title = $('meta[name=wx-share-title]').attr('content');
    var desc = $('meta[name=wx-share-desc]').attr('content');
    var imgUrl = $('meta[name=wx-share-imgUrl]').attr('content');

    //配置相关文件
    wx.config({
        debug: false, // 开启调试模式
        appId: appid, // 必填，公众号的唯一标识
        timestamp: timestamp, // 必填，生成签名的时间戳
        nonceStr: noncestr, // 必填，生成签名的随机串
        signature: signature,// 必填，签名，见附录1
        jsApiList: [
            'onMenuShareTimeline', // 朋友圈
            'onMenuShareAppMessage'// 微信好友/群
        ] // 必填，需要使用的JS接口列表，所有JS接口列表见附录2
    });

    wx.ready(function(){

        // 朋友圈
        wx.onMenuShareTimeline({
            title: title, // 分享标题
            link: share_url,// 分享url
            imgUrl: imgUrl, // 图片url
            success: function (res) {
                $.toast('分享成功', 'text');
            },
            cancel: function () {
                //alert("用户取消分享后执行的回调函数");
            },
            trigger:function(){
                //alert('用户点击分享到朋友圈');
            }
        });

        // 分享给好友/群
        wx.onMenuShareAppMessage({
            title: title, // 分享标题
            desc: desc, // 分享描述
            link: share_url,// 分享url
            imgUrl: imgUrl,// 图片url
            type: 'link', // 分享类型,music、video或link，不填默认为link
            dataUrl: '', // 如果type是music或video，则要提供数据链接，默认为空
            success: function () {
                $.toast('分享成功', 'text');
            },
            cancel: function () {
                // 用户取消分享后执行的回调函数
            }
        });

    });

    wx.error(function(res){
        $.toast('调用微信接口失败', 'text');
    });
}

