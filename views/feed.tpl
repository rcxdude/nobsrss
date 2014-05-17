
<form class="button-form" action="{{c.prefix}}/mark_active" method="post">
    <input type="hidden", name="feed_id", value={{feed.feed_id}}>
    <input type="hidden", name="active", value={{"false" if feed.active else "true"}}>
    <input type="submit", value="Mark {{"Inactive" if feed.active else "Active"}}">
</form>

<form class="button-form" action="{{c.prefix}}/refresh" method="post">
    <input type="hidden" name="feed_id" value="{{feed.feed_id}}">
    <input type="submit" value="Refresh Feed">
</form>

<form class='edit-form' action="{{c.prefix}}/edit_feed" method="post">
    <input type="hidden", name="feed_id", value="{{feed.feed_id}}">
    <div> Name: <input type="text", name="name", value="{{feed.title}}"> </div>
    <div> <a href="{{feed.feed_url}}"> Feed URL: </a>
          <input type="text", name="feed_url", value="{{feed.feed_url}}"> </div>
    <div> <a href="{{feed.site_url}}"> Site URL: </a>
          <input type="text", name="site_url", value="{{feed.site_url}}"> </div>
    <div> <input type="submit", value="Update"> </div>
</form>

<div>
Items:
<ul>
%for item in feed.items:
    <li> <a href={{item.link}}> {{item.title}} </a> ({{item.date}})</li>
%end
</ul>
</div>

%rebase("boilerplate", title=feed.title)
