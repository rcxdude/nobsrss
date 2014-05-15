
<form action="{{c.prefix}}/mark_read" method="post">
    <input type="hidden" name="feed_id" value="all">
    <input type="submit" value="Mark all read">
</form>

<form action="{{c.prefix}}/refresh" method="post">
    <input type="hidden" name="feed_id" value="all">
    <input type="submit" value="Refresh All">
</form>

<ul>
%if refreshing:
<li> Refreshing... </li>
%end
%for unread_feed in unread_feeds:
<li> <a href={{c.prefix}}/feed/{{unread_feed.feed_id}}> {{unread_feed.title}} </a>
    <form class='inline-form' action="{{c.prefix}}/mark_read" method="post">
        <input type="hidden" name="feed_id" value="{{unread_feed.feed_id}}">
        <input type="submit" value="Mark feed read">
    </form>
    <ul>
    %for unread_item in unread_feed.items:
    <li> <a href="{{unread_item.link}}"> {{unread_item.title}} </a> </li>
    %end
    </ul>
</li>
%end
</ul>

%rebase("boilerplate", title='Unread')
