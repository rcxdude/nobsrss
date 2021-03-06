<!DOCTYPE html>
<!--[if lt IE 7]>      <html class="no-js lt-ie9 lt-ie8 lt-ie7"> <![endif]-->
<!--[if IE 7]>         <html class="no-js lt-ie9 lt-ie8"> <![endif]-->
<!--[if IE 8]>         <html class="no-js lt-ie9"> <![endif]-->
<!--[if gt IE 8]><!--> <html class="no-js"> <!--<![endif]-->
    <head>
        <meta charset="utf-8">
        <title>{{title}}</title>
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        %if defined('refresh_time'):
        <meta http-equiv="refresh" content="{{refresh_time}}">
        %end

        <link rel="stylesheet" href="{{c.prefix}}/css/normalize.css">
        <link rel="stylesheet" href="{{c.prefix}}/css/main.css">
        <link rel="stylesheet" href="{{c.prefix}}/css/main_style.css">
        <link rel="shortcut icon" href="{{c.prefix}}/images/favicon.png">
    </head>
    <body>
        <!--[if lt IE 7]>
            <p class="browsehappy">You are using an <strong>outdated</strong> browser. Please <a href="http://browsehappy.com/">upgrade your browser</a> to improve your experience.</p>
        <![endif]-->

        %include("header")

        <section class = "body">
        %include
        </section>
    </body>
</html>
