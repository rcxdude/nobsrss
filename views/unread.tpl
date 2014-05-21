
<form class="button-form" action="{{c.prefix}}/mark_read" method="post">
    <input type="hidden" name="feed_id" value="{{",".join([str(u.feed_id) for u in unread_feeds])}}">
    <input type="submit" value="Mark all read">
</form>

<form class="button-form" action="{{c.prefix}}/refresh" method="post">
    <input type="hidden" name="feed_id" value="all">
    <input type="submit" value="{{"Refreshing..." if refreshing else "Refresh All"}}">
</form>

<ul>
%if not unread_feeds:
<li> All Feed items read! </li>
%else:
%for unread_feed in unread_feeds:
<li class="unread-feed"> 
    <div class="unread-feed-line">
    <a href={{c.prefix}}/feed/{{unread_feed.feed_id}}> {{unread_feed.title}} </a>
    <form class='mark-feed-read' action="{{c.prefix}}/mark_read" method="post">
        <input type="hidden" name="feed_id" value="{{unread_feed.feed_id}}">
        <input type="submit" value="Mark feed read">
    </form>
    </div>
    <ul class='feed-item-list'>
    %for unread_item in unread_feed.items:
    <li> <a href="{{unread_item.link}}"> {{unread_item.title}} </a> </li>
    %end
    </ul>
</li>
%end
%end
</ul>

%n_unread = sum([len(feed.items) for feed in unread_feeds])
%title = 'Unread' + (' ({})'.format(n_unread) if n_unread else '')

%rebase("boilerplate", title=title, refresh_time=600)
