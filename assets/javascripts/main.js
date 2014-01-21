(function() {
  $(document).ready(function() {
    $('body').scrollspy({
      target: '#navigation'
    });
    $('body').on('activate.bs.scrollspy', function() {
      return $(this).addClass('active');
    });
    return $(window).on('load', function() {
      return $('body').scrollspy('refresh');
    });
  });

}).call(this);
