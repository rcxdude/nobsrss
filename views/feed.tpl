
<ul>
<li>
    <form action="{{c.prefix}}/mark_active" method="post">
        <input type="hidden", name="feed_id", value={{feed.feed_id}}>
        <input type="hidden", name="active", value={{"false" if feed.active else "true"}}>
        <input type="submit", value="Mark {{"Inactive" if feed.active else "Active"}}">
    </form>
</li>

<li>
    <form action="{{c.prefix}}/refresh" method="post">
        <input type="hidden" name="feed_id" value="{{feed.feed_id}}">
        <input type="submit" value="Refresh Feed">
    </form>
</li>

<li> Feed URL: <a href="{{feed.feed_url}}"> {{feed.feed_url}} </a> </li>
<li> Site URL: <a href="{{feed.site_url}}"> {{feed.site_url}} </a> </li>
<li>
    <form action="{{c.prefix}}/edit_feed" method="post">
        <input type="hidden", name="feed_id", value="{{feed.feed_id}}">
        Name: <input type="text", name="name", value="{{feed.title}}">
        Feed URL: <input type="text", name="feed_url", value="{{feed.feed_url}}">
        Site URL: <input type="text", name="site_url", value="{{feed.site_url}}">
        <input type="submit", value="Update">
    </form>
</li>
<li> Items:
    <ul>
    %for item in feed.items:
    <li> <a href={{item.link}}> {{item.title}} </a> ({{item.date}})</li>
    %end
    </ul>
</li>
</ul>

%rebase("boilerplate", title=feed.title)
