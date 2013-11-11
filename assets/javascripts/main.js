$(document).ready ->

    ###
    $('nav li').click ->
        $('nav li.selected').find('ul').hide()
        $('nav li.selected').removeClass 'selected'
        $(this).addClass 'selected'

        $(this).find('ul').show()
    ###