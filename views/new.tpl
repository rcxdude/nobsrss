
<form action="{{c.prefix}}/add_feed" method="post">
    <div> Name: <input type="text" name="name"> </div>
    <div> Feed URL: <input type="text" name="feed_url"> </div>
    <div> Site URL: <input type="text" name="site_url"> </div>
    <input type="submit" value="Add Feed">
</form>

%rebase("boilerplate", title='New')
