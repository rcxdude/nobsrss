
<ul>
%for status in statuses:
<li>
    <a href={{c.prefix}}/feed/{{status['feed']}}> {{status['name']}} </a>: 
%if status['active'] == 0:
    INACTIVE
%elif status['last_error'] is None:
    OK
%else:
    <code class="error">
    %for line in status['last_error'].split("\n"):
    {{line}} <br>
    %end
    </code>
%end
</li>
%end
</ul>

%rebase("boilerplate", title='Status')
