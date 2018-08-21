var mySwiper = new Swiper('.swiper-container2', {
  loop: false,
  pagination: '.swiper-pagination2',
});

$("#paging-data-list").on("click", ".comList img", function () {
  var imgBox = $(this).parents(".comList").find("img");
  var i = $(imgBox).index(this);
  $(".big_img .swiper-wrapper").html("");

  for (var index = 0; index < imgBox.length; index++) {
    var imgBigBox = imgBox.eq(index).attr("src").replace("-square.middle", "-square.giant");
    $(".big_img .swiper-wrapper").append('<div class="swiper-slide"><div class="cell"><img src="' + imgBigBox + '" / ></div></div>');
  }
  mySwiper.updateSlidesSize();
  mySwiper.updatePagination();
  $(".big_img").css({
    "z-index": 1001,
    "opacity": "1"
  });
  mySwiper.slideTo(i, 0, false);
  return false;
});

$(".big_img").on("click", function () {
    $(this).css({
      "z-index": "-1",
      "opacity": "0"
    });
});