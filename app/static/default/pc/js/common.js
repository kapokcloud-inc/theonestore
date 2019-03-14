$(document).ready(function(){
  // 购物车加载
  var cart_total = $('#navs_cart_total').text();

  if (cart_total == 0) {
    $('#not-content').addClass('show').removeClass('hide');
    return;
  }

  $.get("/api/cart/", function(res) {
    var ret = res.ret;
    if (ret != 0) {
      return;
    }

    var data = res.data;
    var carts = data.carts;

    $('#cart-total_num').text(data.cart_total);
    $('#cart_amount').text('￥' + data.cart_amount);

    var carts_html = '';
    for (var index = 0; index < carts.length; index++) {
      var cartInfo = carts[index];
      var cart = cartInfo['cart'];
      var item = cartInfo['item'];
      var list_html = '<a class="one-cell" href="/item/' + item.goods_id + '">' +
        '<div class="one-cell_hd avatar">' +
        '<img src="' + item.goods_img + '-square.small" alt="">' +
        '</div>' +
        '<div class="one-cell_bd">' +
        '<p class="all-title">' + item.goods_name + '</p>' +
        '<p class="all-desc">' + item.goods_desc + '</p>' +
        '</div>' +
        '<div class="one-cell_ft mar-left">' +
        '<p class="all-price">￥' + item.goods_price + '</p>' +
        '<p class="all-count">x' + cart.quantity + '</p>' +
        '</div>' +
        '</a>';
      carts_html += list_html;
    }

    $('#navs_carts').append(carts_html);
    return carts_html;

  });

  $('#cart-content').addClass('show').removeClass('hide');
  
});
