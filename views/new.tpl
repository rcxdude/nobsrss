
<form action="{{c.prefix}}/add_feed" method="post">
    Name: <input type="text" name="name">
    Feed URL: <input type="text" name="feed_url">
    Site URL: <input type="text" name="site_url">
    <input type="submit" value="Add Feed">
</form>

%rebase("boilerplate", title='New')
