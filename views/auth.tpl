
<form action="{{c.prefix}}/submit_auth" method="post">
    Password: <input type="password", name="password">
    <input type="submit" value="Login">
</form>

%rebase("boilerplate", title='Login')
